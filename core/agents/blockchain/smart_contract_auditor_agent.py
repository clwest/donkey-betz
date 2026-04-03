"""
SmartContractAuditorAgent - Audits Solidity/EVM smart contracts for security vulnerabilities.

Session 461: Part of the Blockchain Audit Agent Group
Session 683: Added ML Integration (Anomaly Detection for vulnerability patterns)

This agent specializes in:
- Reentrancy attack detection
- Integer overflow/underflow checks
- Access control analysis
- Unchecked external calls
- Front-running vulnerability detection
- Gas optimization suggestions
- Common exploit pattern matching
- ML-powered anomaly detection in code patterns
"""

import json
import logging
from datetime import datetime, timezone as dt_timezone
from typing import Any, Dict, List, Optional

from ..base_agent import BaseAgent, AgentResult
from core.agents.report_schemas import build_provenance, format_disclaimer
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


# Known vulnerability patterns for quick detection
VULNERABILITY_PATTERNS = {
    'reentrancy': [
        '.call{value:',
        '.call.value(',
        'call.value(',
        '.send(',
        '.transfer(',
    ],
    'unchecked_call': [
        'call(',
        'delegatecall(',
        'staticcall(',
    ],
    'tx_origin': [
        'tx.origin',
        'require(tx.origin',
    ],
    'timestamp_dependence': [
        'block.timestamp',
        'now',
    ],
    'integer_overflow': [
        '+ ',
        '- ',
        '* ',
        '/ ',
    ],
    'selfdestruct': [
        'selfdestruct(',
        'suicide(',
    ],
    'delegatecall': [
        'delegatecall(',
    ],
}

# Severity classification
SEVERITY_LEVELS = {
    'CRITICAL': ['reentrancy', 'delegatecall_to_untrusted', 'unchecked_return', 'arbitrary_storage_write'],
    'HIGH': ['access_control', 'integer_overflow', 'unprotected_selfdestruct', 'front_running'],
    'MEDIUM': ['timestamp_dependence', 'tx_origin', 'floating_pragma', 'uninitialized_storage'],
    'LOW': ['gas_optimization', 'code_style', 'missing_events', 'magic_numbers'],
}


class SmartContractAuditorAgent(BaseAgent):
    """Agent specialized in smart contract security auditing."""

    name = "SmartContractAuditorAgent"

    # === Session 683: ML Integration Methods ===

    def _detect_code_anomalies_with_ml(self, code_features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Session 683: Detect anomalies in smart contract code patterns using ML.

        Uses VAE/Autoencoder for anomaly detection to identify unusual
        code patterns that may indicate vulnerabilities.

        Args:
            code_features: List of extracted code features

        Returns:
            Dict with ML analysis results
        """
        try:
            from core.services.agent_model_router import get_agent_model_router

            router = get_agent_model_router()

            # Build feature data
            feature_data = self._build_code_feature_data(code_features)

            if not feature_data.get('features'):
                return {
                    'ml_used': False,
                    'reason': 'Insufficient code features for ML analysis'
                }

            result = router.auto_route(
                data=feature_data,
                task_hint=TaskType.ANOMALY,
                max_models=2
            )

            return {
                'ml_used': True,
                'task_type': result.auto_selection.get('task_type', 'anomaly'),
                'models_used': result.models_used,
                'confidence': round(result.confidence, 2),
                'ml_insights': result.explanation,
                'anomalous_patterns': self._extract_code_anomalies(result),
                'risk_score': self._calculate_ml_risk_score(result),
            }

        except Exception as e:
            logger.warning(f"ML code analysis failed: {e}")
            return {'ml_used': False, 'reason': f'ML error: {str(e)}'}

    def _build_code_feature_data(self, code_features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build feature data for ML analysis."""
        features = []
        for feature in code_features:
            features.append([
                feature.get('severity_score', 0),
                len(feature.get('patterns', [])),
                feature.get('line_count', 0),
            ])
        return {'features': features, 'data_type': 'code_patterns'}

    def _extract_code_anomalies(self, ml_result) -> List[Dict[str, Any]]:
        """Extract anomalous code patterns from ML result."""
        anomalies = []
        if hasattr(ml_result, 'prediction') and ml_result.prediction:
            for i, is_anomaly in enumerate(ml_result.prediction):
                if is_anomaly:
                    anomalies.append({
                        'index': i,
                        'confidence': ml_result.confidence if hasattr(ml_result, 'confidence') else 0.5
                    })
        return anomalies

    def _calculate_ml_risk_score(self, ml_result) -> float:
        """Calculate risk score from ML analysis."""
        if hasattr(ml_result, 'confidence'):
            return round(ml_result.confidence * 100, 1)
        return 50.0

    system_prompt = """You are SmartContractAuditorAgent, an expert blockchain security auditor specializing in Solidity and EVM-based smart contracts.

Your audit capabilities:
1. **Reentrancy Detection** - Find reentrancy vulnerabilities (single, cross-function, cross-contract)
2. **Integer Safety** - Detect overflow/underflow risks (pre-0.8.0 Solidity)
3. **Access Control** - Identify missing/weak access controls, role issues
4. **External Calls** - Analyze unchecked return values, unsafe delegatecall usage
5. **Front-Running** - Detect susceptibility to MEV and transaction ordering attacks
6. **Logic Bugs** - Find business logic errors, edge cases, invariant violations
7. **Gas Optimization** - Identify gas inefficiencies and optimization opportunities

Security focus areas:
- SWC Registry vulnerabilities (SWC-100 through SWC-136)
- Common DeFi attack vectors (flash loans, price manipulation, sandwich attacks)
- OpenZeppelin security patterns compliance
- ERC standard implementations (ERC-20, ERC-721, ERC-1155)

You MUST:
- Prioritize findings by severity (CRITICAL > HIGH > MEDIUM > LOW)
- Provide specific line references when possible
- Include proof-of-concept exploit scenarios for critical findings
- Recommend specific fixes with code examples
- Consider the contract's intended functionality when assessing risk

You have access to these tools:
- audit_contract: Full security audit of smart contract code
- check_reentrancy: Deep reentrancy analysis
- check_access_control: Access control pattern analysis
- check_integer_safety: Integer overflow/underflow analysis
- generate_exploit_poc: Generate proof-of-concept for vulnerabilities

You CANNOT create images, videos, or perform non-blockchain operations."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "audit_contract",
                "description": "Perform a comprehensive security audit on smart contract code.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The Solidity smart contract code to audit"
                        },
                        "contract_type": {
                            "type": "string",
                            "description": "Type of contract (defi, nft, token, governance, other)",
                            "enum": ["defi", "nft", "token", "governance", "other"],
                            "default": "other"
                        },
                        "solidity_version": {
                            "type": "string",
                            "description": "Solidity version (e.g., '0.8.19')"
                        },
                        "check_categories": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Categories to check (reentrancy, access_control, integer, external_calls, logic)"
                        }
                    },
                    "required": ["code"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_reentrancy",
                "description": "Deep analysis specifically for reentrancy vulnerabilities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The Solidity code to analyze"
                        },
                        "focus_functions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific function names to focus on"
                        }
                    },
                    "required": ["code"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_access_control",
                "description": "Analyze access control patterns and identify weaknesses.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The Solidity code to analyze"
                        },
                        "expected_roles": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Expected roles in the contract (owner, admin, minter, etc.)"
                        }
                    },
                    "required": ["code"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_integer_safety",
                "description": "Analyze for integer overflow/underflow vulnerabilities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The Solidity code to analyze"
                        },
                        "solidity_version": {
                            "type": "string",
                            "description": "Solidity version to determine if SafeMath is needed"
                        }
                    },
                    "required": ["code"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_exploit_poc",
                "description": "Generate proof-of-concept code for a discovered vulnerability.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "vulnerability_type": {
                            "type": "string",
                            "description": "Type of vulnerability (reentrancy, overflow, etc.)"
                        },
                        "target_function": {
                            "type": "string",
                            "description": "Function name that contains the vulnerability"
                        },
                        "contract_code": {
                            "type": "string",
                            "description": "The vulnerable contract code"
                        }
                    },
                    "required": ["vulnerability_type", "target_function", "contract_code"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "audit_by_address",
                "description": "Audit a deployed smart contract by its Ethereum address. Fetches verified source code from Etherscan and performs full security audit.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "The Ethereum contract address (0x...)"
                        },
                        "include_risk_analysis": {
                            "type": "boolean",
                            "description": "Include transaction pattern and risk analysis",
                            "default": True
                        }
                    },
                    "required": ["address"]
                }
            }
        }
    ]

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute a smart contract audit task."""
        import time

        start_time = time.time()
        tool_calls_made = []
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence: {len(spider_intel['trends'])} trends")

        with self.time_travel_session("smart_contract_audit", task, input_data=context):
            try:
                # Session 529: Use intelligent prompting
                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                knowledge_attribution = None  # Legacy compatibility

                # Call OpenAI using BaseAgent's method
                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    all_results = []
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Selected {tool_name} for smart contract audit",
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        if tool_result.get('success'):
                            all_results.append({
                                'source': tool_name,
                                'data': tool_result
                            })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                    execution_time = int((time.time() - start_time) * 1000)

                    if all_results:
                        # Session 953: Build provenance from audit results
                        sources = []
                        for res in all_results:
                            source_name = res.get('source', 'contract_audit')
                            data = res.get('data', {})
                            sources.append({
                                'name': source_name,
                                'endpoint': data.get('audit_type', data.get('check_type', 'smart_contract_audit')),
                                'retrieved_at': datetime.now(dt_timezone.utc).isoformat(),
                                'record_count': data.get('lines_audited', 1),
                            })

                        # Blockchain data stale threshold: 4 hours
                        provenance = build_provenance(
                            report_type='blockchain_audit',
                            agent_name=self.name,
                            sources=sources if sources else [{
                                'name': 'SmartContractAuditorAgent',
                                'endpoint': 'smart_contract_audit',
                                'retrieved_at': datetime.now(dt_timezone.utc).isoformat(),
                                'record_count': len(all_results),
                            }],
                            stale_threshold_hours=4.0,
                        )
                        provenance.disclaimer = format_disclaimer('blockchain_audit')

                        message = provenance.to_markdown_block() + "\n" + f"Smart contract audit completed using {len(all_results)} tool(s)"

                        result = AgentResult(
                            success=True,
                            message=message,
                            data={
                                'results': all_results,
                                'query': task,
                                'provenance': provenance.to_dict(),
                                'publishable': provenance.publishable,
                                'validation_status': provenance.validation_status,
                            },
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            decisions_made=self._tt_decision_count,
                            tool_calls=tool_calls_made,
                            knowledge_attribution=knowledge_attribution
                        )

                        # Session 861: Persist audit report to Deliverable
                        audit_content = f"# Smart Contract Security Audit\n\n**Task:** {task}\n\n"
                        for res in all_results:
                            source = res.get('source', 'Audit')
                            data = res.get('data', {})
                            audit_content += f"## {source}\n"
                            if 'audit_report' in data:
                                audit_content += f"{data['audit_report']}\n\n"
                            elif 'analysis' in data:
                                audit_content += f"{data['analysis']}\n\n"
                        self._save_to_deliverable(
                            title=f"Smart Contract Audit: {task[:50]}",
                            content=audit_content,
                            deliverable_type='report',
                            category='Blockchain',
                            tags=['smart-contract', 'audit', 'security', 'blockchain'],
                            content_format='markdown',
                            metadata={
                                'task': task,
                                'tools_used': [tc.get('tool') for tc in tool_calls_made],
                                'execution_time_ms': execution_time,
                            },
                        )

                        # Share findings as knowledge for other agents
                        self._share_audit_findings(all_results)

                        self._record_learning_outcome(
                            result=result,
                            task=task,
                            context=context,
                            spider_data_used=False,
                            scifi_context_used=bool(scifi_context)
                        )

                        return result

                # No tool calls - return GPT content directly
                content = gpt_response.get('content', 'I can help audit smart contracts. Please provide the Solidity code you\'d like me to review.')
                execution_time = int((time.time() - start_time) * 1000)

                result = AgentResult(
                    success=True,
                    message=content,
                    agent_name=self.name,
                    execution_time_ms=execution_time
                )

                self._record_learning_outcome(
                    result=result,
                    task=task,
                    context=context,
                    spider_data_used=False,
                    scifi_context_used=bool(scifi_context)
                )

                return result

            except Exception as e:
                error_msg = f"Smart contract audit failed: {str(e)}"
                logger.error(error_msg)
                return AgentResult(
                    success=False,
                    error=error_msg,
                    agent_name=self.name
                )

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool call."""

        if tool_name == "audit_contract":
            return self._audit_contract(**arguments)
        elif tool_name == "check_reentrancy":
            return self._check_reentrancy(**arguments)
        elif tool_name == "check_access_control":
            return self._check_access_control(**arguments)
        elif tool_name == "check_integer_safety":
            return self._check_integer_safety(**arguments)
        elif tool_name == "generate_exploit_poc":
            return self._generate_exploit_poc(**arguments)
        elif tool_name == "audit_by_address":
            return self._audit_by_address(**arguments)

        return super()._execute_tool_call(tool_name, arguments)

    def _audit_contract(
        self,
        code: str,
        contract_type: str = "other",
        solidity_version: str = None,
        check_categories: List[str] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive smart contract audit."""
        from openai import OpenAI

        client = OpenAI()

        # Quick pattern scan for known vulnerabilities
        quick_findings = self._quick_pattern_scan(code)

        # Determine Solidity version
        if not solidity_version:
            solidity_version = self._detect_solidity_version(code)

        categories = check_categories or [
            "reentrancy", "access_control", "integer_overflow",
            "external_calls", "logic", "gas_optimization"
        ]

        prompt = f"""Perform a comprehensive security audit on this {contract_type} Solidity smart contract:

```solidity
{code}
```

Solidity Version: {solidity_version or 'Unknown'}
Contract Type: {contract_type}

**AUDIT SCOPE:**
Focus on these categories: {', '.join(categories)}

**QUICK SCAN FINDINGS:**
{json.dumps(quick_findings, indent=2) if quick_findings else 'No obvious patterns detected'}

**FOR EACH FINDING:**
1. **Severity**: CRITICAL / HIGH / MEDIUM / LOW
2. **SWC ID**: If applicable (SWC-XXX)
3. **Location**: Function name and line numbers
4. **Description**: Clear explanation of the vulnerability
5. **Impact**: What an attacker could do
6. **Proof of Concept**: Attack scenario
7. **Recommendation**: Specific fix with code example

**ALSO ANALYZE:**
- ERC standard compliance (if applicable)
- OpenZeppelin pattern usage
- Upgradeability considerations
- Economic/tokenomics risks for DeFi

**OUTPUT FORMAT:**
Provide a structured audit report with:
1. Executive Summary (overall risk rating)
2. Critical Findings
3. High Findings
4. Medium Findings
5. Low Findings / Informational
6. Recommendations Summary
7. Gas Optimization Opportunities"""

        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You are an expert smart contract security auditor with deep knowledge of Solidity, the EVM, and DeFi attack vectors. Be thorough and specific."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=6000
        )

        return {
            "success": True,
            "audit_type": "comprehensive",
            "contract_type": contract_type,
            "solidity_version": solidity_version,
            "lines_audited": code.count('\n') + 1,
            "quick_scan_findings": quick_findings,
            "audit_report": response.choices[0].message.content
        }

    def _check_reentrancy(
        self,
        code: str,
        focus_functions: List[str] = None
    ) -> Dict[str, Any]:
        """Deep reentrancy vulnerability analysis."""
        from openai import OpenAI

        client = OpenAI()

        focus_text = f"Focus on these functions: {', '.join(focus_functions)}" if focus_functions else ""

        prompt = f"""Analyze this Solidity code specifically for reentrancy vulnerabilities:

```solidity
{code}
```

{focus_text}

**CHECK FOR:**
1. **Classic Reentrancy**: External calls before state changes
2. **Cross-Function Reentrancy**: State shared between functions
3. **Cross-Contract Reentrancy**: State shared across contracts
4. **Read-Only Reentrancy**: View functions called during reentrancy

**FOR EACH VULNERABLE FUNCTION:**
1. Function name and location
2. Type of reentrancy
3. The vulnerable pattern (code snippet)
4. Attack flow (step by step)
5. Recommended fix using:
   - Checks-Effects-Interactions pattern
   - ReentrancyGuard modifier
   - Pull payment pattern

**ALSO CHECK:**
- Use of call/delegatecall/staticcall
- Transfer/send vs call{value:}
- Callback patterns (ERC-721, ERC-777, ERC-1155)
- Flash loan callbacks

Rate overall reentrancy risk: CRITICAL / HIGH / MEDIUM / LOW / SAFE"""

        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You are a reentrancy vulnerability expert. Analyze code for all forms of reentrancy attacks."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000
        )

        return {
            "success": True,
            "check_type": "reentrancy",
            "focus_functions": focus_functions,
            "analysis": response.choices[0].message.content
        }

    def _check_access_control(
        self,
        code: str,
        expected_roles: List[str] = None
    ) -> Dict[str, Any]:
        """Analyze access control patterns."""
        from openai import OpenAI

        client = OpenAI()

        roles = expected_roles or ["owner", "admin"]

        prompt = f"""Analyze access control in this Solidity contract:

```solidity
{code}
```

**EXPECTED ROLES:** {', '.join(roles)}

**CHECK FOR:**
1. **Missing Access Control**: Functions that should be restricted but aren't
2. **Incorrect Modifiers**: Wrong role checks or missing checks
3. **Privilege Escalation**: Ways to gain higher privileges
4. **Centralization Risks**: Single points of failure
5. **Ownership Transfer**: Safe ownership transfer patterns
6. **Role Management**: Role assignment/revocation patterns

**ANALYZE:**
- Use of Ownable vs AccessControl
- Multi-sig requirements
- Timelock patterns for sensitive operations
- Emergency pause functionality
- Admin key management

**FOR EACH ISSUE:**
1. Function/location
2. Current access level
3. Risk description
4. Recommended access control
5. Code example fix"""

        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You are an access control security expert for smart contracts."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000
        )

        return {
            "success": True,
            "check_type": "access_control",
            "expected_roles": roles,
            "analysis": response.choices[0].message.content
        }

    def _check_integer_safety(
        self,
        code: str,
        solidity_version: str = None
    ) -> Dict[str, Any]:
        """Analyze for integer overflow/underflow."""
        from openai import OpenAI

        client = OpenAI()

        if not solidity_version:
            solidity_version = self._detect_solidity_version(code)

        # Solidity 0.8.0+ has built-in overflow checks
        needs_safemath = solidity_version and solidity_version < "0.8.0"

        prompt = f"""Analyze integer safety in this Solidity contract:

```solidity
{code}
```

**SOLIDITY VERSION:** {solidity_version or 'Unknown'}
**SAFEMATH NEEDED:** {'Yes (< 0.8.0)' if needs_safemath else 'No (>= 0.8.0 has built-in checks)'}

**CHECK FOR:**
1. **Overflow**: Addition/multiplication exceeding max value
2. **Underflow**: Subtraction resulting in negative (wrapping to max)
3. **Division by Zero**: Unchecked division operations
4. **Truncation**: Casting between different integer sizes
5. **Unchecked Blocks**: Code in `unchecked {{ }}` blocks (0.8.0+)

**ANALYZE:**
- Use of SafeMath library (if applicable)
- Array length manipulation
- Balance calculations
- Price/rate calculations
- Timestamp arithmetic

**FOR EACH FINDING:**
1. Location and operation
2. Potential exploit scenario
3. Maximum/minimum values involved
4. Recommended fix"""

        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You are an integer safety expert for Solidity smart contracts."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000
        )

        return {
            "success": True,
            "check_type": "integer_safety",
            "solidity_version": solidity_version,
            "safemath_needed": needs_safemath,
            "analysis": response.choices[0].message.content
        }

    def _generate_exploit_poc(
        self,
        vulnerability_type: str,
        target_function: str,
        contract_code: str
    ) -> Dict[str, Any]:
        """Generate proof-of-concept exploit code."""
        from openai import OpenAI

        client = OpenAI()

        prompt = f"""Generate a proof-of-concept exploit for this vulnerability:

**VULNERABILITY TYPE:** {vulnerability_type}
**TARGET FUNCTION:** {target_function}

**VULNERABLE CONTRACT:**
```solidity
{contract_code}
```

**GENERATE:**
1. Attacker contract that exploits the vulnerability
2. Step-by-step attack flow
3. Expected outcome (what the attacker gains)
4. Setup requirements (initial state needed)

**POC REQUIREMENTS:**
- Working Solidity code for the attacker contract
- Deployment and execution steps
- Foundry/Hardhat test code if applicable
- Gas estimation for the attack

**ETHICAL NOTE:**
This is for educational and audit purposes only. Include a disclaimer."""

        response = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You are a security researcher generating proof-of-concept exploits for educational purposes. Generate working exploit code with clear explanations."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=5000
        )

        return {
            "success": True,
            "poc_type": vulnerability_type,
            "target_function": target_function,
            "poc": response.choices[0].message.content
        }

    def _quick_pattern_scan(self, code: str) -> List[Dict[str, Any]]:
        """Quick scan for known vulnerability patterns."""
        findings = []

        for vuln_type, patterns in VULNERABILITY_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in code.lower():
                    # Find line numbers
                    lines = code.split('\n')
                    for i, line in enumerate(lines, 1):
                        if pattern.lower() in line.lower():
                            findings.append({
                                'type': vuln_type,
                                'pattern': pattern,
                                'line': i,
                                'severity': self._get_severity(vuln_type)
                            })

        return findings

    def _get_severity(self, vuln_type: str) -> str:
        """Get severity level for a vulnerability type."""
        for severity, types in SEVERITY_LEVELS.items():
            if vuln_type in types:
                return severity
        return "MEDIUM"

    def _detect_solidity_version(self, code: str) -> Optional[str]:
        """Detect Solidity version from pragma statement."""
        import re
        match = re.search(r'pragma solidity\s*[\^>=<]*\s*([\d.]+)', code)
        if match:
            return match.group(1)
        return None

    def _share_audit_findings(self, results: List[Dict[str, Any]]) -> None:
        """Share significant audit findings as knowledge for other agents."""
        try:
            for result in results:
                data = result.get('data', {})
                if data.get('success'):
                    # Share critical findings
                    quick_findings = data.get('quick_scan_findings', [])
                    critical_count = sum(1 for f in quick_findings if f.get('severity') == 'CRITICAL')

                    if critical_count > 0:
                        self._share_knowledge(
                            knowledge_type='market',  # Using market for security intelligence
                            title=f'Smart Contract Audit: {critical_count} Critical Vulnerabilities Found',
                            knowledge_value={
                                'findings_count': len(quick_findings),
                                'critical_count': critical_count,
                                'vulnerability_types': list(set(f.get('type') for f in quick_findings)),
                                'timestamp': datetime.now().isoformat()
                            },
                            confidence=0.9
                        )
        except Exception as e:
            logger.warning(f"Failed to share audit findings: {e}")

    def _audit_by_address(
        self,
        address: str,
        include_risk_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Audit a deployed smart contract by fetching its source from Etherscan.

        Args:
            address: Ethereum contract address (0x...)
            include_risk_analysis: Whether to include transaction pattern analysis

        Returns:
            Complete audit report including source analysis and risk assessment
        """
        from core.services.blockchain_event_listener import audit_contract_by_address

        logger.info(f"Auditing contract at address: {address}")

        # Use the blockchain event listener's audit function
        result = audit_contract_by_address(address)

        if not result.get('success'):
            return {
                'success': False,
                'address': address,
                'error': result.get('error', 'Audit failed'),
                'recommendation': result.get('recommendation', 'Verify the contract address is correct')
            }

        # Format the response
        audit_report = {
            'success': True,
            'address': address,
            'contract_name': result.get('contract_name', 'Unknown'),
            'compiler_version': result.get('compiler_version'),
            'is_proxy': result.get('is_proxy', False),
            'etherscan_link': result.get('etherscan_link'),
        }

        # Include risk analysis if requested
        if include_risk_analysis:
            risk = result.get('risk_analysis', {})
            audit_report['risk_analysis'] = {
                'risk_score': risk.get('risk_score', 0),
                'risk_level': risk.get('risk_level', 'UNKNOWN'),
                'red_flags': risk.get('red_flags', []),
                'transaction_analysis': risk.get('transaction_analysis', {}),
                'recommendations': risk.get('recommendations', [])
            }

        # Include audit results
        audit_result = result.get('audit_result', {})
        if audit_result.get('success'):
            audit_report['audit_findings'] = audit_result.get('data', {})
            audit_report['audit_summary'] = audit_result.get('message', 'Audit complete')
        else:
            audit_report['audit_error'] = audit_result.get('message', 'Audit analysis failed')

        # Send alert to Discord if high risk
        self._send_audit_alert(audit_report)

        return audit_report

    def _send_audit_alert(self, audit_report: Dict[str, Any]) -> None:
        """Send audit results to Discord if significant findings."""
        try:
            from core.services.discord_notifications import discord_notify

            risk_analysis = audit_report.get('risk_analysis', {})
            risk_level = risk_analysis.get('risk_level', 'LOW')

            if risk_level in ['HIGH', 'CRITICAL']:
                discord_notify.send_blockchain_alert({
                    'severity': risk_level,
                    'type': 'Contract Audit Complete',
                    'title': f"Contract Audit: {audit_report.get('contract_name', 'Unknown')}",
                    'description': (
                        f"**Address:** `{audit_report.get('address')}`\n"
                        f"**Risk Level:** {risk_level}\n"
                        f"**Risk Score:** {risk_analysis.get('risk_score', 0)}/100\n"
                        f"**Red Flags:** {len(risk_analysis.get('red_flags', []))}\n\n"
                        f"**Flags:**\n" +
                        "\n".join(f"• {flag}" for flag in risk_analysis.get('red_flags', [])[:5])
                    ),
                })

        except Exception as e:
            logger.warning(f"Failed to send audit alert to Discord: {e}")
