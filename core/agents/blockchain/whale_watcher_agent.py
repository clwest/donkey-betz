"""
WhaleWatcherAgent - Monitors large token movements and whale activity.

Session 461: Part of the Blockchain Audit Agent Group
Session 683: Added ML Integration (GNN for wallet transaction network analysis)

This agent specializes in:
- Tracking large value transfers (whale movements)
- Monitoring token holder distribution changes
- Detecting accumulation/distribution patterns
- Alerting on significant exchange flows
- Tracking known whale addresses
- ML-powered wallet network analysis (GNN) - Session 683
"""

import json
import logging
from datetime import datetime, timezone as dt_timezone
from typing import Any, Dict

from ..base_agent import BaseAgent, AgentResult
from core.agents.report_schemas import build_provenance, format_disclaimer
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

logger = logging.getLogger(__name__)


# Whale thresholds by token type
WHALE_THRESHOLDS = {
    'ETH': 1000,      # 1000 ETH (~$3M at $3000/ETH)
    'WETH': 1000,
    'USDC': 1000000,  # $1M
    'USDT': 1000000,
    'DAI': 1000000,
    'WBTC': 50,       # 50 WBTC (~$2.5M at $50k/BTC)
    'default': 500000  # $500k USD equivalent
}

# Known whale categories
WHALE_CATEGORIES = {
    'exchange': ['binance', 'coinbase', 'kraken', 'ftx', 'kucoin'],
    'defi_protocol': ['aave', 'compound', 'makerdao', 'uniswap'],
    'whale_fund': ['3ac', 'alameda', 'jump', 'wintermute'],
    'government': ['us_seized', 'uk_seized'],
    'unknown': []
}


class WhaleWatcherAgent(BaseAgent):
    """Agent specialized in monitoring whale movements and large transfers."""

    name = "WhaleWatcherAgent"

    system_prompt = """You are WhaleWatcherAgent, an expert at tracking large cryptocurrency movements and whale behavior.

Your monitoring capabilities:
1. **Large Transfer Detection** - Identify transfers above whale thresholds
2. **Accumulation Tracking** - Detect addresses accumulating tokens
3. **Distribution Analysis** - Identify selling/distribution patterns
4. **Exchange Flow Monitoring** - Track deposits/withdrawals from exchanges
5. **Holder Analysis** - Monitor changes in top holder positions
6. **Correlation Analysis** - Find patterns across multiple whale addresses

Market impact analysis:
- Large exchange deposits often precede selling pressure
- Large exchange withdrawals suggest accumulation/holding
- Whale wallet activity can signal market direction
- Coordinated whale movements may indicate insider activity

You MUST:
- Quantify movements in both token amounts and USD value
- Identify the source/destination category (exchange, DeFi, unknown)
- Consider market impact potential
- Track historical patterns for known addresses
- Generate alerts for significant movements

You have access to these tools:
- monitor_large_transfers: Watch for transfers above thresholds
- analyze_whale_wallet: Deep analysis of a whale address
- track_exchange_flows: Monitor exchange deposit/withdrawal patterns
- detect_accumulation: Identify accumulation patterns
- generate_whale_alert: Create alert for significant whale activity

You CANNOT create images, videos, or perform non-blockchain operations."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "monitor_large_transfers",
                "description": "Monitor for large token transfers above whale thresholds.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "token": {
                            "type": "string",
                            "description": "Token to monitor (ETH, USDC, etc.)"
                        },
                        "threshold_usd": {
                            "type": "number",
                            "description": "Minimum value in USD to track",
                            "default": 500000
                        },
                        "time_window_hours": {
                            "type": "integer",
                            "description": "Hours to look back",
                            "default": 24
                        },
                        "exclude_contracts": {
                            "type": "boolean",
                            "description": "Exclude known contract addresses",
                            "default": False
                        }
                    },
                    "required": ["token"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_whale_wallet",
                "description": "Deep analysis of a whale wallet address.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "Wallet address to analyze"
                        },
                        "include_history": {
                            "type": "boolean",
                            "description": "Include transaction history analysis",
                            "default": True
                        },
                        "include_holdings": {
                            "type": "boolean",
                            "description": "Include current holdings breakdown",
                            "default": True
                        }
                    },
                    "required": ["address"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "track_exchange_flows",
                "description": "Monitor deposit/withdrawal flows for exchanges.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "exchange": {
                            "type": "string",
                            "description": "Exchange to track (binance, coinbase, kraken, all)",
                            "default": "all"
                        },
                        "token": {
                            "type": "string",
                            "description": "Token to track (ETH, BTC, USDC, all)",
                            "default": "ETH"
                        },
                        "time_window_hours": {
                            "type": "integer",
                            "description": "Hours to analyze",
                            "default": 24
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "detect_accumulation",
                "description": "Detect accumulation or distribution patterns.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "Address to analyze (or 'top_holders' for general analysis)"
                        },
                        "token": {
                            "type": "string",
                            "description": "Token to analyze"
                        },
                        "time_window_days": {
                            "type": "integer",
                            "description": "Days to analyze",
                            "default": 7
                        }
                    },
                    "required": ["token"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_whale_alert",
                "description": "Generate an alert for significant whale activity.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "alert_type": {
                            "type": "string",
                            "description": "Type of whale activity",
                            "enum": ["large_transfer", "exchange_deposit", "exchange_withdrawal", "accumulation", "distribution", "unknown_whale"]
                        },
                        "token": {
                            "type": "string",
                            "description": "Token involved"
                        },
                        "amount": {
                            "type": "number",
                            "description": "Amount transferred"
                        },
                        "usd_value": {
                            "type": "number",
                            "description": "USD value"
                        },
                        "from_address": {
                            "type": "string",
                            "description": "Source address"
                        },
                        "to_address": {
                            "type": "string",
                            "description": "Destination address"
                        },
                        "market_impact": {
                            "type": "string",
                            "description": "Expected market impact",
                            "enum": ["BULLISH", "BEARISH", "NEUTRAL", "UNKNOWN"]
                        }
                    },
                    "required": ["alert_type", "token", "amount", "usd_value"]
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
        """Execute a whale watching task."""
        import time

        start_time = time.time()
        tool_calls_made = []
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence: {len(spider_intel['trends'])} trends")

        with self.time_travel_session("whale_watch", task, input_data=context):
            try:
                # Session 529: Use intelligent prompting
                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                knowledge_attribution = None  # Legacy compatibility

                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    all_results = []
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Selected {tool_name} for whale monitoring",
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
                        # Session 683: Run ML analysis on wallet transaction data
                        ml_insights = self._analyze_wallet_network_with_ml(all_results)

                        # Session 953: Build provenance from analysis results
                        sources = []
                        for res in all_results:
                            source_name = res.get('source', 'whale_analysis')
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
                                'name': 'WhaleWatcherAgent',
                                'endpoint': 'blockchain_api',
                                'retrieved_at': datetime.now(dt_timezone.utc).isoformat(),
                                'record_count': len(all_results),
                            }],
                            stale_threshold_hours=4.0,
                        )
                        provenance.disclaimer = format_disclaimer('blockchain_audit')

                        message = provenance.to_markdown_block() + "\n" + f"Whale monitoring completed with {len(all_results)} analysis(es)"

                        result = AgentResult(
                            success=True,
                            message=message,
                            data={
                                'results': all_results,
                                'query': task,
                                'ml_analysis': ml_insights,  # Session 683: Add ML analysis
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

                        # Session 861: Persist analysis to Deliverable
                        analysis_content = f"# Whale Monitoring Report\n\n**Task:** {task}\n\n"
                        for res in all_results:
                            source = res.get('source', 'Analysis')
                            data = res.get('data', {})
                            analysis_content += f"## {source}\n{data}\n\n"
                        self._save_to_deliverable(
                            title=f"Whale Watch: {task[:50]}",
                            content=analysis_content,
                            deliverable_type='analysis',
                            category='Blockchain',
                            tags=['whale', 'monitoring', 'blockchain', 'analysis'],
                            content_format='markdown',
                            metadata={
                                'task': task,
                                'analyses': len(all_results),
                            },
                        )

                        # Record learning outcome for collective intelligence
                        try:
                            self._record_learning_outcome(
                                task=task,
                                result=result,
                                success=True,
                                context={
                                    'agent_type': self.__class__.__name__,
                                    'execution_time_ms': execution_time,
                                    'analyses_completed': len(all_results),
                                    'tools_used': [tc['tool'] for tc in tool_calls_made],
                                }
                            )
                        except Exception as le:
                            logger.warning(f"Failed to record learning outcome: {le}")

                        return result

                content = gpt_response.get('content', 'I can help monitor whale activity. Specify a token, address, or exchange to track.')
                return AgentResult(
                    success=True,
                    message=content,
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

            except Exception as e:
                logger.error(f"Whale monitoring failed: {e}")
                result = AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name
                )

                # Record failed learning outcome
                try:
                    self._record_learning_outcome(
                        task=task,
                        result=result,
                        success=False,
                        context={
                            'agent_type': self.__class__.__name__,
                            'error': str(e),
                        }
                    )
                except Exception as le:
                    logger.warning(f"Failed to record learning outcome: {le}")

                return result

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool call."""

        if tool_name == "monitor_large_transfers":
            return self._monitor_large_transfers(**arguments)
        elif tool_name == "analyze_whale_wallet":
            return self._analyze_whale_wallet(**arguments)
        elif tool_name == "track_exchange_flows":
            return self._track_exchange_flows(**arguments)
        elif tool_name == "detect_accumulation":
            return self._detect_accumulation(**arguments)
        elif tool_name == "generate_whale_alert":
            return self._generate_whale_alert(**arguments)

        return super()._execute_tool_call(tool_name, arguments)

    # Per-request timeout for GPT-5-mini tool calls (seconds).
    # Prevents unbounded hangs when multiple tool calls run sequentially.
    _LLM_TIMEOUT = 60

    def _get_llm_client(self):
        """Get an OpenAI client with proper connection-level timeout."""
        return get_openai_client()

    def _monitor_large_transfers(
        self,
        token: str,
        threshold_usd: float = 500000,
        time_window_hours: int = 24,
        exclude_contracts: bool = False
    ) -> Dict[str, Any]:
        """Monitor for large transfers."""
        client = self._get_llm_client()

        # Get token-specific threshold
        token_threshold = WHALE_THRESHOLDS.get(token.upper(), WHALE_THRESHOLDS['default'])

        prompt = f"""Analyze large {token} transfers for whale activity:

**MONITORING PARAMETERS:**
- Token: {token}
- Minimum USD Value: ${threshold_usd:,.0f}
- Time Window: Last {time_window_hours} hours
- Token-specific threshold: {token_threshold} {token}
- Exclude contracts: {exclude_contracts}

**WHALE THRESHOLDS:**
{json.dumps(WHALE_THRESHOLDS, indent=2)}

**ANALYSIS FRAMEWORK:**
1. Identify transfers above threshold
2. Categorize source/destination:
   - Exchange (hot wallet, cold storage)
   - DeFi Protocol (Aave, Compound, Uniswap)
   - Known Whale
   - Unknown/New Whale
3. Assess market impact potential
4. Look for patterns (multiple transfers, splitting)

**OUTPUT:**
1. Summary of large transfers detected
2. Top 5 most significant transfers
3. Net exchange flow (in vs out)
4. Market sentiment indicator (BULLISH/BEARISH/NEUTRAL)
5. Addresses to watch"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are a whale movement analyst. Track large crypto transfers and assess market impact."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000,
            timeout=self._LLM_TIMEOUT,
        )

        return {
            "success": True,
            "monitoring_type": "large_transfers",
            "token": token,
            "threshold_usd": threshold_usd,
            "time_window_hours": time_window_hours,
            "analysis": response.choices[0].message.content
        }

    def _analyze_whale_wallet(
        self,
        address: str,
        include_history: bool = True,
        include_holdings: bool = True
    ) -> Dict[str, Any]:
        """Deep analysis of a whale wallet."""
        client = self._get_llm_client()

        prompt = f"""Analyze this whale wallet address:

**ADDRESS:** {address}

**ANALYSIS SCOPE:**
- Transaction History: {include_history}
- Current Holdings: {include_holdings}

**ANALYZE:**
1. **Identity**: Known entity? Exchange? Fund? Protocol?
2. **Holdings Profile**: Token distribution, concentration
3. **Behavior Pattern**: Trading style, timing, frequency
4. **Historical Performance**: Past profitable trades
5. **Risk Indicators**: Connections to scams/hacks
6. **Market Influence**: Size relative to token markets

**WHALE CATEGORIES:**
{json.dumps(WHALE_CATEGORIES, indent=2)}

**OUTPUT:**
1. Wallet identity/category
2. Current holdings summary
3. Recent activity summary
4. Behavior classification (trader, holder, smart money)
5. Follow recommendation (WATCH / IGNORE / ALERT)"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are a whale wallet analyst. Identify, categorize, and assess whale addresses."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000,
            timeout=self._LLM_TIMEOUT,
        )

        return {
            "success": True,
            "analysis_type": "whale_wallet",
            "address": address,
            "analysis": response.choices[0].message.content
        }

    def _track_exchange_flows(
        self,
        exchange: str = "all",
        token: str = "ETH",
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """Track exchange deposit/withdrawal flows."""
        client = self._get_llm_client()

        prompt = f"""Analyze exchange flows for {token}:

**PARAMETERS:**
- Exchange: {exchange}
- Token: {token}
- Time Window: {time_window_hours} hours

**KNOWN EXCHANGES:**
{json.dumps(WHALE_CATEGORIES['exchange'], indent=2)}

**ANALYSIS:**
1. **Net Flow**: Total deposits vs withdrawals
2. **Deposit Analysis**:
   - Large deposits (selling pressure indicator)
   - Source addresses (whale? retail? defi?)
3. **Withdrawal Analysis**:
   - Large withdrawals (accumulation indicator)
   - Destination patterns
4. **Cross-Exchange Flows**: Movement between exchanges
5. **Historical Comparison**: vs 7-day, 30-day averages

**MARKET SIGNALS:**
- High net deposits = potential selling pressure
- High net withdrawals = accumulation/bullish
- Stable flows = consolidation

**OUTPUT:**
1. Net flow summary (deposit-heavy vs withdrawal-heavy)
2. Top deposit sources
3. Top withdrawal destinations
4. Market sentiment indicator
5. 24h change in exchange balance"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are an exchange flow analyst. Track crypto movements in/out of exchanges."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000,
            timeout=self._LLM_TIMEOUT,
        )

        return {
            "success": True,
            "analysis_type": "exchange_flows",
            "exchange": exchange,
            "token": token,
            "time_window_hours": time_window_hours,
            "analysis": response.choices[0].message.content
        }

    def _detect_accumulation(
        self,
        token: str,
        address: str = None,
        time_window_days: int = 7
    ) -> Dict[str, Any]:
        """Detect accumulation or distribution patterns."""
        client = self._get_llm_client()

        target = address if address else "top holders"

        prompt = f"""Detect accumulation/distribution patterns for {token}:

**PARAMETERS:**
- Token: {token}
- Target: {target}
- Time Window: {time_window_days} days

**ACCUMULATION INDICATORS:**
- Consistent buying over time
- Withdrawal from exchanges
- Increasing wallet balance
- Smart money addresses accumulating

**DISTRIBUTION INDICATORS:**
- Consistent selling over time
- Deposits to exchanges
- Decreasing wallet balance
- Early investors selling

**ANALYZE:**
1. Balance changes over time window
2. Transaction frequency and direction
3. Source/destination patterns
4. Correlation with price movement
5. Whale behavior vs retail

**OUTPUT:**
1. Pattern detected: ACCUMULATION / DISTRIBUTION / NEUTRAL
2. Confidence level (0-100%)
3. Key addresses involved
4. Volume analysis
5. Market implication"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are a crypto accumulation pattern analyst. Detect buying and selling patterns."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000,
            timeout=self._LLM_TIMEOUT,
        )

        return {
            "success": True,
            "analysis_type": "accumulation_detection",
            "token": token,
            "target": target,
            "time_window_days": time_window_days,
            "analysis": response.choices[0].message.content
        }

    def _generate_whale_alert(
        self,
        alert_type: str,
        token: str,
        amount: float,
        usd_value: float,
        from_address: str = None,
        to_address: str = None,
        market_impact: str = "UNKNOWN"
    ) -> Dict[str, Any]:
        """Generate whale movement alert."""

        alert = {
            "success": True,
            "alert": {
                "type": "whale_movement",
                "subtype": alert_type,
                "token": token,
                "amount": amount,
                "usd_value": usd_value,
                "from_address": from_address,
                "to_address": to_address,
                "market_impact": market_impact,
                "timestamp": datetime.now().isoformat()
            }
        }

        # Determine severity based on USD value
        if usd_value >= 10000000:  # $10M+
            alert['alert']['severity'] = 'CRITICAL'
        elif usd_value >= 1000000:  # $1M+
            alert['alert']['severity'] = 'HIGH'
        elif usd_value >= 500000:  # $500k+
            alert['alert']['severity'] = 'MEDIUM'
        else:
            alert['alert']['severity'] = 'LOW'

        logger.info(f"WHALE ALERT: {amount:,.2f} {token} (${usd_value:,.0f}) - {alert_type}")

        # Share as knowledge
        try:
            self._share_knowledge(
                knowledge_type='market',
                title=f"Whale Alert: {amount:,.0f} {token} ({alert_type})",
                knowledge_value=alert['alert'],
                confidence=0.9
            )
        except Exception as e:
            logger.debug(f"Could not share whale knowledge: {e}")

        # Try Discord notification
        try:
            from core.services.discord_notifications import discord_notify
            discord_notify.send_whale_alert(alert['alert'])
        except Exception as e:
            logger.debug(f"Could not send Discord whale alert: {e}")

        return alert

    # =========================================================================
    # SESSION 683: ML INTEGRATION - GNN FOR WALLET NETWORK ANALYSIS
    # =========================================================================

    def _analyze_wallet_network_with_ml(self, results: list) -> Dict[str, Any]:
        """
        Use ML models to analyze wallet transaction networks.

        Session 683: Integrates the Agent-Model Router to auto-select GNN
        for analyzing wallet-to-wallet transaction relationships.
        """
        try:
            from core.services.agent_model_router import get_agent_model_router

            # Build graph data from transaction results
            graph_data = self._build_wallet_graph(results)

            if not graph_data.get('nodes') or len(graph_data['nodes']) < 2:
                return {
                    'ml_used': False,
                    'reason': 'Insufficient wallet data for network analysis'
                }

            # Get router and run auto-selection (should select GNN for graph data)
            router = get_agent_model_router()
            result = router.auto_route(graph_data, max_models=2)

            return {
                'ml_used': True,
                'task_type': result.auto_selection.get('task_type', 'unknown'),
                'models_used': result.models_used,
                'confidence': round(result.confidence, 2),
                'ml_insights': result.explanation,
                'selection_reason': result.auto_selection.get('selection_reason', ''),
                'wallet_count': len(graph_data['nodes']),
                'transaction_count': len(graph_data['edges']),
            }

        except ImportError as e:
            logger.warning(f"ML router not available: {e}")
            return {'ml_used': False, 'reason': f'ML not available: {e}'}
        except Exception as e:
            logger.warning(f"ML analysis error: {e}")
            return {'ml_used': False, 'reason': f'ML error: {e}'}

    def _build_wallet_graph(self, results: list) -> Dict[str, Any]:
        """
        Build graph representation of wallet transaction networks.

        Creates nodes for wallets and edges for transactions between them.
        """
        nodes = []
        edges = []
        node_ids = set()

        for result_item in results:
            data = result_item.get('data', {})

            # Extract from_address and to_address from various result types
            from_addr = data.get('from_address')
            to_addr = data.get('to_address')

            if from_addr:
                if from_addr not in node_ids:
                    nodes.append({
                        'id': from_addr,
                        'type': 'wallet',
                        'label': f"{from_addr[:8]}..."
                    })
                    node_ids.add(from_addr)

            if to_addr:
                if to_addr not in node_ids:
                    nodes.append({
                        'id': to_addr,
                        'type': 'wallet',
                        'label': f"{to_addr[:8]}..."
                    })
                    node_ids.add(to_addr)

            # Create edge for transaction
            if from_addr and to_addr:
                edges.append([from_addr, to_addr])

            # Also extract from alert data if present
            alert_data = data.get('alert', {})
            alert_from = alert_data.get('from_address')
            alert_to = alert_data.get('to_address')

            if alert_from and alert_from not in node_ids:
                nodes.append({
                    'id': alert_from,
                    'type': 'whale',
                    'usd_value': alert_data.get('usd_value'),
                    'label': f"🐋 {alert_from[:8]}..."
                })
                node_ids.add(alert_from)

            if alert_to and alert_to not in node_ids:
                nodes.append({
                    'id': alert_to,
                    'type': 'destination',
                    'label': f"{alert_to[:8]}..."
                })
                node_ids.add(alert_to)

            if alert_from and alert_to:
                edges.append([alert_from, alert_to])

        # Add known exchange wallets as nodes if they appear in context
        for exchange in WHALE_CATEGORIES.get('exchange', []):
            exchange_id = f"exchange_{exchange}"
            if exchange_id not in node_ids:
                nodes.append({
                    'id': exchange_id,
                    'type': 'exchange',
                    'name': exchange,
                    'label': f"🏦 {exchange}"
                })
                node_ids.add(exchange_id)

        return {
            'nodes': nodes,
            'edges': edges
        }
