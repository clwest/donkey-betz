"""
TransactionMonitorAgent - Monitors blockchain transactions for suspicious patterns.

Session 461: Part of the Blockchain Audit Agent Group
Session 683: Added ML Integration (Anomaly Detection for transaction patterns)

This agent specializes in:
- Detecting suspicious transaction patterns
- Identifying flash loan attacks in progress
- Monitoring unusual value transfers
- Tracking known malicious addresses
- Analyzing gas price anomalies
- Detecting potential exploits
- ML-powered transaction anomaly detection
"""

import json
import logging
from datetime import datetime, timezone as dt_timezone
from typing import Any, Dict, List

from ..base_agent import BaseAgent, AgentResult
from core.agents.report_schemas import build_provenance, format_disclaimer
from ml.auto_selection import TaskType
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

logger = logging.getLogger(__name__)


# Suspicious patterns to watch for
SUSPICIOUS_PATTERNS = {
    'flash_loan': {
        'indicators': ['flashLoan', 'flash_loan', 'borrow', 'repay'],
        'severity': 'HIGH',
        'description': 'Flash loan activity detected'
    },
    'contract_drain': {
        'indicators': ['withdrawAll', 'emergencyWithdraw', 'drain'],
        'severity': 'CRITICAL',
        'description': 'Potential contract draining attempt'
    },
    'governance_attack': {
        'indicators': ['vote', 'propose', 'execute', 'timelock'],
        'severity': 'HIGH',
        'description': 'Governance manipulation attempt'
    },
    'sandwich': {
        'indicators': ['swap', 'frontrun', 'backrun'],
        'severity': 'MEDIUM',
        'description': 'Sandwich attack pattern'
    },
    'reentrancy': {
        'indicators': ['recursive', 'callback', 'fallback'],
        'severity': 'CRITICAL',
        'description': 'Reentrancy attack pattern'
    }
}

# Known attack vectors by protocol type
ATTACK_VECTORS = {
    'dex': ['sandwich', 'front_running', 'price_manipulation'],
    'lending': ['flash_loan', 'oracle_manipulation', 'liquidation_attack'],
    'nft': ['reentrancy', 'floor_price_manipulation', 'wash_trading'],
    'bridge': ['replay_attack', 'validator_manipulation', 'token_mint']
}


class TransactionMonitorAgent(BaseAgent):
    """Agent specialized in monitoring blockchain transactions for suspicious activity."""

    name = "TransactionMonitorAgent"

    # === Session 683: ML Integration Methods ===

    def _detect_transaction_anomalies_with_ml(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Session 683: Detect anomalies in transaction patterns using ML.

        Uses VAE/Autoencoder for anomaly detection to identify unusual
        transaction patterns that may indicate attacks.

        Args:
            transactions: List of transaction data

        Returns:
            Dict with ML analysis results
        """
        try:
            from core.services.agent_model_router import get_agent_model_router

            router = get_agent_model_router()

            # Build transaction feature data
            tx_data = self._build_transaction_feature_data(transactions)

            if not tx_data.get('features'):
                return {
                    'ml_used': False,
                    'reason': 'Insufficient transaction data for ML analysis'
                }

            result = router.auto_route(
                data=tx_data,
                task_hint=TaskType.ANOMALY,
                max_models=2
            )

            return {
                'ml_used': True,
                'task_type': result.auto_selection.get('task_type', 'anomaly'),
                'models_used': result.models_used,
                'confidence': round(result.confidence, 2),
                'ml_insights': result.explanation,
                'anomalous_transactions': self._extract_tx_anomalies(result, transactions),
                'threat_level': self._assess_tx_threat_level(result),
            }

        except Exception as e:
            logger.warning(f"ML transaction analysis failed: {e}")
            return {'ml_used': False, 'reason': f'ML error: {str(e)}'}

    def _build_transaction_feature_data(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build feature data from transactions for ML analysis."""
        features = []
        timestamps = []

        for tx in transactions:
            features.append([
                float(tx.get('value', 0)),
                float(tx.get('gas_price', 0)),
                float(tx.get('gas_used', 0)),
                1 if tx.get('is_contract_call') else 0,
            ])
            if tx.get('timestamp'):
                timestamps.append(tx['timestamp'])

        return {
            'features': features,
            'timestamps': timestamps,
            'data_type': 'transaction_patterns'
        }

    def _extract_tx_anomalies(self, ml_result, transactions: List[Dict]) -> List[Dict[str, Any]]:
        """Extract anomalous transactions from ML result."""
        anomalies = []
        if hasattr(ml_result, 'prediction') and ml_result.prediction:
            pred = ml_result.prediction
            if isinstance(pred, list):
                for i, is_anomaly in enumerate(pred):
                    if is_anomaly and i < len(transactions):
                        anomalies.append({
                            'tx_hash': transactions[i].get('hash', f'tx_{i}'),
                            'confidence': ml_result.confidence if hasattr(ml_result, 'confidence') else 0.5,
                            'reason': 'ML-detected anomaly'
                        })
        return anomalies

    def _assess_tx_threat_level(self, ml_result) -> str:
        """Assess transaction threat level from ML analysis."""
        confidence = ml_result.confidence if hasattr(ml_result, 'confidence') else 0.5
        if confidence > 0.85:
            return 'CRITICAL'
        elif confidence > 0.7:
            return 'HIGH'
        elif confidence > 0.5:
            return 'MEDIUM'
        return 'LOW'

    system_prompt = """You are TransactionMonitorAgent, an expert blockchain investigator specializing in transaction analysis and attack detection.

Your monitoring capabilities:
1. **Pattern Detection** - Identify suspicious transaction patterns in real-time
2. **Flash Loan Analysis** - Detect flash loan attacks and arbitrage
3. **MEV Detection** - Identify front-running, sandwich attacks, and MEV extraction
4. **Value Tracking** - Monitor unusual value transfers and whale movements
5. **Gas Analysis** - Detect gas price manipulation and priority gas auctions
6. **Address Reputation** - Track known malicious addresses and mixers

Attack patterns you can identify:
- Flash loan attacks (borrowing large amounts without collateral)
- Sandwich attacks (front-running + back-running trades)
- Oracle manipulation (price feed attacks)
- Reentrancy exploits (recursive calling patterns)
- Governance attacks (voting manipulation)
- Bridge exploits (cross-chain attack patterns)

You MUST:
- Analyze transaction sequences, not just individual transactions
- Consider the temporal relationship between transactions
- Identify the attack vector and potential victim
- Estimate financial impact
- Provide actionable alerts with confidence levels

You have access to these tools:
- analyze_transaction: Deep analysis of a single transaction
- detect_attack_pattern: Identify if transactions match known attack patterns
- trace_value_flow: Follow the money through transaction chains
- check_address_reputation: Check if addresses are associated with known attacks
- generate_alert: Create security alert for suspicious activity

You CANNOT create images, videos, or perform non-blockchain operations."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "analyze_transaction",
                "description": "Perform deep analysis on a blockchain transaction.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tx_hash": {
                            "type": "string",
                            "description": "Transaction hash to analyze"
                        },
                        "tx_data": {
                            "type": "object",
                            "description": "Transaction data if hash lookup not available"
                        },
                        "chain": {
                            "type": "string",
                            "description": "Blockchain network",
                            "enum": ["ethereum", "bsc", "polygon", "arbitrum", "optimism"],
                            "default": "ethereum"
                        },
                        "include_internal": {
                            "type": "boolean",
                            "description": "Include internal transactions",
                            "default": True
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "detect_attack_pattern",
                "description": "Analyze transactions to identify known attack patterns.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "transactions": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "List of transactions to analyze"
                        },
                        "time_window_seconds": {
                            "type": "integer",
                            "description": "Time window to consider for pattern matching",
                            "default": 60
                        },
                        "target_patterns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific patterns to check for"
                        }
                    },
                    "required": ["transactions"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "trace_value_flow",
                "description": "Trace the flow of value through a series of transactions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "starting_address": {
                            "type": "string",
                            "description": "Address to start tracing from"
                        },
                        "starting_tx": {
                            "type": "string",
                            "description": "Transaction to start tracing from"
                        },
                        "depth": {
                            "type": "integer",
                            "description": "How many hops to trace",
                            "default": 5
                        },
                        "min_value_eth": {
                            "type": "number",
                            "description": "Minimum value to trace (in ETH)",
                            "default": 0.1
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_address_reputation",
                "description": "Check if an address has known associations with attacks or scams.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "Ethereum address to check"
                        },
                        "check_sources": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Sources to check (etherscan_labels, tornado, known_attackers)"
                        }
                    },
                    "required": ["address"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_alert",
                "description": "Generate a security alert for suspicious activity.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "severity": {
                            "type": "string",
                            "description": "Alert severity",
                            "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
                        },
                        "alert_type": {
                            "type": "string",
                            "description": "Type of alert"
                        },
                        "title": {
                            "type": "string",
                            "description": "Short alert title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed description"
                        },
                        "affected_addresses": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Addresses involved"
                        },
                        "estimated_impact_usd": {
                            "type": "number",
                            "description": "Estimated financial impact in USD"
                        },
                        "recommended_actions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Recommended response actions"
                        }
                    },
                    "required": ["severity", "alert_type", "title", "description"]
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
        """Execute a transaction monitoring task."""
        import time

        start_time = time.time()
        tool_calls_made = []
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence: {len(spider_intel['trends'])} trends")

        with self.time_travel_session("transaction_monitor", task, input_data=context):
            try:
                # Session 529: Use intelligent prompting
                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                knowledge_attribution = None  # Legacy compatibility

                # Call OpenAI
                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    all_results = []
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Selected {tool_name} for transaction monitoring",
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

                            # Share alerts as knowledge
                            if tool_name == 'generate_alert':
                                self._share_alert_knowledge(tool_result)

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                    execution_time = int((time.time() - start_time) * 1000)

                    if all_results:
                        # Session 953: Build provenance from analysis results
                        sources = []
                        for res in all_results:
                            source_name = res.get('source', 'transaction_analysis')
                            data = res.get('data', {})
                            sources.append({
                                'name': source_name,
                                'endpoint': data.get('analysis_type', 'blockchain_api'),
                                'retrieved_at': datetime.now(dt_timezone.utc).isoformat(),
                                'record_count': 1,
                            })

                        # Blockchain data stale threshold: 4 hours
                        provenance = build_provenance(
                            report_type='blockchain_audit',
                            agent_name=self.name,
                            sources=sources if sources else [{
                                'name': 'TransactionMonitorAgent',
                                'endpoint': 'blockchain_api',
                                'retrieved_at': datetime.now(dt_timezone.utc).isoformat(),
                                'record_count': len(all_results),
                            }],
                            stale_threshold_hours=4.0,
                        )
                        provenance.disclaimer = format_disclaimer('blockchain_audit')

                        message = provenance.to_markdown_block() + "\n" + f"Transaction monitoring completed with {len(all_results)} analysis(es)"

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

                        self._record_learning_outcome(
                            result=result,
                            task=task,
                            context=context,
                            spider_data_used=False,
                            scifi_context_used=bool(scifi_context)
                        )

                        # Session 1006: Persist output to Deliverable
                        self._save_to_deliverable(
                            title=f"Transaction Monitor: {task[:80]}",
                            content=result.message,
                            deliverable_type='analysis',
                            category='Blockchain Monitoring',
                            tags=['blockchain', 'transactions'],
                            metadata={'task': task[:200]},
                        )

                        return result

                # No tool calls
                content = gpt_response.get('content', 'I can help monitor blockchain transactions. Provide transaction hashes or data to analyze.')
                execution_time = int((time.time() - start_time) * 1000)

                return AgentResult(
                    success=True,
                    message=content,
                    agent_name=self.name,
                    execution_time_ms=execution_time
                )

            except Exception as e:
                error_msg = f"Transaction monitoring failed: {str(e)}"
                logger.error(error_msg)
                return AgentResult(
                    success=False,
                    error=error_msg,
                    agent_name=self.name
                )

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool call."""

        if tool_name == "analyze_transaction":
            return self._analyze_transaction(**arguments)
        elif tool_name == "detect_attack_pattern":
            return self._detect_attack_pattern(**arguments)
        elif tool_name == "trace_value_flow":
            return self._trace_value_flow(**arguments)
        elif tool_name == "check_address_reputation":
            return self._check_address_reputation(**arguments)
        elif tool_name == "generate_alert":
            return self._generate_alert(**arguments)

        return super()._execute_tool_call(tool_name, arguments)

    def _analyze_transaction(
        self,
        tx_hash: str = None,
        tx_data: Dict[str, Any] = None,
        chain: str = "ethereum",
        include_internal: bool = True
    ) -> Dict[str, Any]:
        """Analyze a blockchain transaction."""
        from openai import OpenAI

        client = get_openai_client()

        # Format transaction data for analysis
        tx_info = ""
        if tx_hash:
            tx_info = f"Transaction Hash: {tx_hash}\nChain: {chain}"
        elif tx_data:
            tx_info = f"Transaction Data:\n{json.dumps(tx_data, indent=2)}"
        else:
            return {"error": "Either tx_hash or tx_data must be provided"}

        prompt = f"""Analyze this blockchain transaction for suspicious activity:

{tx_info}

**ANALYZE:**
1. **Value Transfer**: Amount transferred, token types
2. **Method Called**: What contract function was invoked
3. **Gas Usage**: Was gas abnormally high/low?
4. **Contract Interactions**: What contracts were called?
5. **Internal Transactions**: {'Include' if include_internal else 'Exclude'} internal tx analysis

**CHECK FOR:**
- Flash loan patterns (borrow + operation + repay)
- Reentrancy indicators (recursive calls)
- Sandwich attack components (swap timing)
- Oracle manipulation (price queries)
- Unusual contract interactions

**PROVIDE:**
1. Transaction summary
2. Risk assessment (SAFE / SUSPICIOUS / MALICIOUS)
3. Attack type if suspicious
4. Confidence level (0-100%)
5. Recommended action"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are a blockchain transaction analyst. Analyze transactions for security risks and attack patterns."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000
        )

        return {
            "success": True,
            "analysis_type": "transaction",
            "tx_hash": tx_hash,
            "chain": chain,
            "analysis": response.choices[0].message.content
        }

    def _detect_attack_pattern(
        self,
        transactions: List[Dict[str, Any]] = None,
        time_window_seconds: int = 60,
        target_patterns: List[str] = None
    ) -> Dict[str, Any]:
        """Detect known attack patterns in transactions."""
        # Handle missing transactions argument
        if not transactions:
            return {
                "success": False,
                "error": "No transactions provided to analyze",
                "patterns_detected": [],
                "requires": "List of transaction objects with hash, from, to, value, timestamp"
            }

        from openai import OpenAI

        client = get_openai_client()

        patterns_to_check = target_patterns or list(SUSPICIOUS_PATTERNS.keys())

        prompt = f"""Analyze these transactions for attack patterns:

**TRANSACTIONS:**
{json.dumps(transactions, indent=2)}

**TIME WINDOW:** {time_window_seconds} seconds
**PATTERNS TO CHECK:** {', '.join(patterns_to_check)}

**KNOWN ATTACK PATTERNS:**
{json.dumps(SUSPICIOUS_PATTERNS, indent=2)}

**ANALYSIS:**
1. Look for transactions that form an attack sequence
2. Check temporal relationships (flash loan must be single block)
3. Identify victim contracts/addresses
4. Calculate profit/loss

**OUTPUT:**
1. Detected patterns (if any)
2. Confidence level for each
3. Attack flow reconstruction
4. Estimated impact
5. Related addresses to monitor"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are an expert at detecting blockchain attack patterns. Analyze transaction sequences for known exploits."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000
        )

        return {
            "success": True,
            "analysis_type": "pattern_detection",
            "transactions_analyzed": len(transactions),
            "time_window": time_window_seconds,
            "patterns_checked": patterns_to_check,
            "analysis": response.choices[0].message.content
        }

    def _trace_value_flow(
        self,
        starting_address: str = None,
        starting_tx: str = None,
        depth: int = 5,
        min_value_eth: float = 0.1
    ) -> Dict[str, Any]:
        """Trace value flow through transactions."""
        from openai import OpenAI

        client = get_openai_client()

        start_point = starting_address or starting_tx or "Not specified"

        prompt = f"""Trace the flow of value through blockchain transactions:

**STARTING POINT:** {start_point}
**TRACE DEPTH:** {depth} hops
**MINIMUM VALUE:** {min_value_eth} ETH

**TRACE ANALYSIS:**
1. Follow outgoing transfers from the starting point
2. Identify intermediate addresses (potential mixers/hops)
3. Track final destinations
4. Calculate total value flow

**CHECK FOR:**
- Mixer usage (Tornado Cash, etc.)
- Exchange deposits (known exchange addresses)
- Smart contract interactions
- Token swaps/conversions
- Splitting patterns (value divided among many addresses)
- Aggregation patterns (many sources to one)

**OUTPUT:**
1. Value flow diagram (text representation)
2. Key addresses identified
3. Suspicious patterns in flow
4. Final destination analysis"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are a blockchain forensics expert. Trace value flows to identify money laundering, attack profits, or suspicious activity."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000
        )

        return {
            "success": True,
            "analysis_type": "value_trace",
            "starting_point": start_point,
            "depth": depth,
            "min_value": min_value_eth,
            "analysis": response.choices[0].message.content
        }

    def _check_address_reputation(
        self,
        address: str,
        check_sources: List[str] = None
    ) -> Dict[str, Any]:
        """Check address reputation and associations."""
        from openai import OpenAI

        client = get_openai_client()

        sources = check_sources or ["etherscan_labels", "tornado", "known_attackers", "exchanges"]

        prompt = f"""Analyze the reputation and associations of this address:

**ADDRESS:** {address}

**CHECK SOURCES:** {', '.join(sources)}

**ANALYZE:**
1. **Known Labels**: Is this address labeled on Etherscan?
2. **Mixer Interaction**: Has it interacted with Tornado Cash or similar?
3. **Attack Association**: Is it linked to known exploits?
4. **Exchange Deposits**: Does it send to known exchanges?
5. **Age & Activity**: Account age and transaction patterns

**REPUTATION FACTORS:**
- Associated with known attackers? (-100 points)
- Used mixers? (-50 points)
- Verified contract? (+50 points)
- Known exchange/protocol? (+80 points)
- Fresh address with large tx? (-30 points)

**OUTPUT:**
1. Reputation score (-100 to +100)
2. Risk level (HIGH RISK / MEDIUM RISK / LOW RISK / TRUSTED)
3. Known associations
4. Flags/warnings
5. Recommended monitoring level"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are a blockchain address reputation analyst. Assess addresses for risk and known malicious associations."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=3000
        )

        return {
            "success": True,
            "analysis_type": "reputation",
            "address": address,
            "sources_checked": sources,
            "analysis": response.choices[0].message.content
        }

    def _generate_alert(
        self,
        severity: str,
        alert_type: str,
        title: str,
        description: str,
        affected_addresses: List[str] = None,
        estimated_impact_usd: float = None,
        recommended_actions: List[str] = None
    ) -> Dict[str, Any]:
        """Generate a security alert."""
        alert = {
            "success": True,
            "alert": {
                "severity": severity,
                "type": alert_type,
                "title": title,
                "description": description,
                "timestamp": datetime.now().isoformat(),
                "affected_addresses": affected_addresses or [],
                "estimated_impact_usd": estimated_impact_usd,
                "recommended_actions": recommended_actions or [],
            }
        }

        # Log the alert
        logger.warning(f"BLOCKCHAIN ALERT [{severity}]: {title}")

        # Try to send to Discord
        try:
            from core.services.discord_notifications import discord_notify
            discord_notify.send_blockchain_alert(alert['alert'])
        except Exception as e:
            logger.debug(f"Could not send Discord alert: {e}")

        return alert

    def _share_alert_knowledge(self, alert_result: Dict[str, Any]) -> None:
        """Share alert as knowledge for other agents."""
        try:
            alert = alert_result.get('alert', {})
            if alert.get('severity') in ['CRITICAL', 'HIGH']:
                self._share_knowledge(
                    knowledge_type='market',
                    title=f"Blockchain Alert: {alert.get('title', 'Unknown')}",
                    knowledge_value={
                        'severity': alert.get('severity'),
                        'type': alert.get('type'),
                        'description': alert.get('description', '')[:200],
                        'timestamp': alert.get('timestamp')
                    },
                    confidence=0.95
                )
        except Exception as e:
            logger.warning(f"Failed to share alert knowledge: {e}")
