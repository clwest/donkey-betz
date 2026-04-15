"""
Blockchain Event Listener Service
=================================

Session 461: Real-time blockchain event monitoring for the Audit Agent Group

This service:
- Listens for new blocks and transactions via Etherscan API
- Detects whale movements, suspicious patterns, and new contract deployments
- Triggers appropriate audit agents when events are detected
- Posts alerts to Discord #blockchain-agents channel

Event Types:
- WHALE_TRANSFER: Large ETH/token movements
- CONTRACT_DEPLOY: New contract deployments
- SUSPICIOUS_TX: Unusual transaction patterns
- EXPLOIT_SIGNATURE: Known exploit pattern detected
"""

import os
import logging
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import requests

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of blockchain events we monitor."""
    WHALE_TRANSFER = "whale_transfer"
    CONTRACT_DEPLOY = "contract_deploy"
    SUSPICIOUS_TX = "suspicious_tx"
    EXPLOIT_SIGNATURE = "exploit_signature"
    LARGE_TOKEN_TRANSFER = "large_token_transfer"
    FLASH_LOAN = "flash_loan"


@dataclass
class BlockchainEvent:
    """Represents a detected blockchain event."""
    event_type: EventType
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    data: Dict[str, Any]
    timestamp: datetime
    tx_hash: Optional[str] = None
    address: Optional[str] = None
    block_number: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': self.event_type.value,
            'severity': self.severity,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'tx_hash': self.tx_hash,
            'address': self.address,
            'block_number': self.block_number,
        }


class BlockchainEventListener:
    """
    Listens for blockchain events and triggers audit agents.

    Usage:
        listener = BlockchainEventListener()
        listener.add_handler(EventType.WHALE_TRANSFER, my_handler)
        listener.start()
    """

    # Etherscan API V2 (V1 deprecated Dec 2025)
    ETHERSCAN_API = "https://api.etherscan.io/v2/api"
    CHAIN_ID = 1  # Ethereum mainnet

    # Thresholds
    WHALE_THRESHOLD_ETH = 100  # 100 ETH
    LARGE_TOKEN_THRESHOLD_USD = 100000  # $100k

    # Polling interval (seconds) - respect API rate limits
    POLL_INTERVAL = 15  # 4 calls/minute = safe for free tier

    # Known exploit signatures (contract bytecode patterns)
    EXPLOIT_SIGNATURES = {
        'reentrancy_attack': '0x5b5e139f',  # Example signature
        'flash_loan_attack': '0xddf252ad',  # ERC20 Transfer signature (used in flash loans)
    }

    # Known malicious addresses (would be regularly updated)
    KNOWN_MALICIOUS = set()

    def __init__(self):
        self.api_key = os.environ.get('ETHERSCAN_API_KEY', '')
        self.handlers: Dict[EventType, List[Callable]] = {et: [] for et in EventType}
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self._last_block = 0
        self._processed_txs: set = set()  # Avoid duplicate processing

        if not self.api_key:
            logger.warning("ETHERSCAN_API_KEY not set - event listener will have limited functionality")

    def add_handler(self, event_type: EventType, handler: Callable[[BlockchainEvent], None]) -> None:
        """Register a handler for a specific event type."""
        self.handlers[event_type].append(handler)
        logger.info(f"Added handler for {event_type.value} events")

    def remove_handler(self, event_type: EventType, handler: Callable) -> None:
        """Remove a handler."""
        if handler in self.handlers[event_type]:
            self.handlers[event_type].remove(handler)

    def start(self) -> None:
        """Start the event listener in a background thread."""
        if self.running:
            logger.warning("Event listener already running")
            return

        self.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Blockchain event listener started")

    def stop(self) -> None:
        """Stop the event listener."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Blockchain event listener stopped")

    def _run_loop(self) -> None:
        """Main polling loop."""
        while self.running:
            try:
                self._poll_for_events()
            except Exception as e:
                logger.error(f"Event polling error: {e}")

            time.sleep(self.POLL_INTERVAL)

    def _poll_for_events(self) -> None:
        """Poll Etherscan for new events."""
        if not self.api_key:
            return

        # Get latest block
        current_block = self._get_latest_block()
        if current_block <= self._last_block:
            return

        logger.debug(f"Checking blocks {self._last_block + 1} to {current_block}")

        # Check for whale transfers
        whale_events = self._check_whale_transfers()
        for event in whale_events:
            self._dispatch_event(event)

        # Check for new contract deployments
        deploy_events = self._check_contract_deployments()
        for event in deploy_events:
            self._dispatch_event(event)

        # Update last processed block
        self._last_block = current_block

    def _get_latest_block(self) -> int:
        """Get the latest block number."""
        try:
            response = requests.get(
                self.ETHERSCAN_API,
                params={
                    'chainid': self.CHAIN_ID,
                    'module': 'proxy',
                    'action': 'eth_blockNumber',
                    'apikey': self.api_key
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('result'):
                    return int(data['result'], 16)
        except Exception as e:
            logger.warning(f"Error getting latest block: {e}")
        return self._last_block

    def _check_whale_transfers(self) -> List[BlockchainEvent]:
        """Check for whale-level ETH transfers."""
        events = []

        # Monitor known exchange addresses
        monitored = {
            'binance_hot': '0x28C6c06298d514Db089934071355E5743bf21d60',
            'coinbase': '0x71660c4005BA85c37ccec55d0C4493E66Fe775d3',
        }

        for label, address in monitored.items():
            try:
                response = requests.get(
                    self.ETHERSCAN_API,
                    params={
                        'chainid': self.CHAIN_ID,
                        'module': 'account',
                        'action': 'txlist',
                        'address': address,
                        'startblock': max(0, self._last_block - 100),
                        'endblock': 99999999,
                        'page': 1,
                        'offset': 5,
                        'sort': 'desc',
                        'apikey': self.api_key
                    },
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == '1' and data.get('result'):
                        for tx in data['result']:
                            tx_hash = tx.get('hash')
                            if tx_hash in self._processed_txs:
                                continue

                            value_eth = int(tx.get('value', 0)) / 1e18

                            if value_eth >= self.WHALE_THRESHOLD_ETH:
                                events.append(BlockchainEvent(
                                    event_type=EventType.WHALE_TRANSFER,
                                    severity='HIGH' if value_eth >= 1000 else 'MEDIUM',
                                    data={
                                        'from': tx.get('from'),
                                        'to': tx.get('to'),
                                        'value_eth': value_eth,
                                        'address_label': label,
                                        'gas_used': tx.get('gasUsed'),
                                    },
                                    timestamp=datetime.fromtimestamp(
                                        int(tx.get('timeStamp', 0)),
                                        tz=timezone.utc
                                    ),
                                    tx_hash=tx_hash,
                                    address=address,
                                    block_number=int(tx.get('blockNumber', 0))
                                ))
                                self._processed_txs.add(tx_hash)

                                # Keep processed set bounded
                                if len(self._processed_txs) > 10000:
                                    self._processed_txs = set(list(self._processed_txs)[-5000:])

            except Exception as e:
                logger.warning(f"Error checking whale transfers for {label}: {e}")

        return events

    def _check_contract_deployments(self) -> List[BlockchainEvent]:
        """Check for new contract deployments."""
        events = []

        try:
            # Get recent internal transactions (contract creations)
            response = requests.get(
                self.ETHERSCAN_API,
                params={
                    'chainid': self.CHAIN_ID,
                    'module': 'account',
                    'action': 'txlistinternal',
                    'startblock': max(0, self._last_block - 50),
                    'endblock': 99999999,
                    'page': 1,
                    'offset': 10,
                    'sort': 'desc',
                    'apikey': self.api_key
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1' and data.get('result'):
                    for tx in data['result']:
                        # Contract creation has empty 'to' or specific type
                        if tx.get('type') == 'create' or not tx.get('to'):
                            tx_hash = tx.get('hash')
                            if tx_hash in self._processed_txs:
                                continue

                            contract_address = tx.get('contractAddress', '')

                            events.append(BlockchainEvent(
                                event_type=EventType.CONTRACT_DEPLOY,
                                severity='MEDIUM',
                                data={
                                    'deployer': tx.get('from'),
                                    'contract_address': contract_address,
                                    'value_eth': int(tx.get('value', 0)) / 1e18,
                                },
                                timestamp=datetime.fromtimestamp(
                                    int(tx.get('timeStamp', 0)),
                                    tz=timezone.utc
                                ),
                                tx_hash=tx_hash,
                                address=contract_address,
                                block_number=int(tx.get('blockNumber', 0))
                            ))
                            self._processed_txs.add(tx_hash)

        except Exception as e:
            logger.warning(f"Error checking contract deployments: {e}")

        return events

    def _dispatch_event(self, event: BlockchainEvent) -> None:
        """Dispatch event to registered handlers."""
        handlers = self.handlers.get(event.event_type, [])

        logger.info(f"Dispatching {event.event_type.value} event (severity: {event.severity})")

        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Handler error for {event.event_type.value}: {e}")

        # Also dispatch to the default Discord handler
        self._send_to_discord(event)

    def _send_to_discord(self, event: BlockchainEvent) -> None:
        """Send event to Discord #blockchain-agents channel."""
        try:
            from core.services.discord_notifications import discord_notify

            # Format alert based on event type
            if event.event_type == EventType.WHALE_TRANSFER:
                discord_notify.send_whale_alert({
                    'severity': event.severity,
                    'from': event.data.get('from', 'Unknown'),
                    'to': event.data.get('to', 'Unknown'),
                    'value_eth': event.data.get('value_eth', 0),
                    'tx_hash': event.tx_hash,
                    'address_label': event.data.get('address_label', ''),
                })
            else:
                discord_notify.send_blockchain_alert({
                    'severity': event.severity,
                    'type': event.event_type.value,
                    'title': f"{event.event_type.value.replace('_', ' ').title()}",
                    'description': self._format_event_description(event),
                    'tx_hash': event.tx_hash,
                    'address': event.address,
                })

        except Exception as e:
            logger.warning(f"Failed to send Discord alert: {e}")

    def _format_event_description(self, event: BlockchainEvent) -> str:
        """Format event description for Discord."""
        if event.event_type == EventType.CONTRACT_DEPLOY:
            return (f"New contract deployed\n"
                   f"**Deployer:** `{event.data.get('deployer', 'Unknown')[:20]}...`\n"
                   f"**Contract:** `{event.address[:20]}...`\n"
                   f"**Block:** {event.block_number}")

        elif event.event_type == EventType.SUSPICIOUS_TX:
            return (f"Suspicious transaction detected\n"
                   f"**Pattern:** {event.data.get('pattern', 'Unknown')}\n"
                   f"**Risk Score:** {event.data.get('risk_score', 'N/A')}")

        return f"Event data: {event.data}"

    # =========================================================================
    # Contract Audit Methods
    # =========================================================================

    def fetch_contract_source(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Fetch verified contract source code from Etherscan.

        Returns:
            Dict with contract info including source code, ABI, compiler version
        """
        if not self.api_key:
            return {'error': 'Etherscan API key not configured'}

        try:
            response = requests.get(
                self.ETHERSCAN_API,
                params={
                    'chainid': self.CHAIN_ID,
                    'module': 'contract',
                    'action': 'getsourcecode',
                    'address': address,
                    'apikey': self.api_key
                },
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1' and data.get('result'):
                    result = data['result'][0]

                    # Check if contract is verified
                    if not result.get('SourceCode'):
                        return {
                            'verified': False,
                            'address': address,
                            'error': 'Contract source code not verified on Etherscan'
                        }

                    return {
                        'verified': True,
                        'address': address,
                        'contract_name': result.get('ContractName', 'Unknown'),
                        'source_code': result.get('SourceCode', ''),
                        'abi': result.get('ABI', ''),
                        'compiler_version': result.get('CompilerVersion', ''),
                        'optimization_used': result.get('OptimizationUsed', ''),
                        'runs': result.get('Runs', ''),
                        'constructor_arguments': result.get('ConstructorArguments', ''),
                        'library': result.get('Library', ''),
                        'proxy': result.get('Proxy', '0') == '1',
                        'implementation': result.get('Implementation', ''),
                    }

            return {'error': f'API error: {response.status_code}'}

        except Exception as e:
            logger.error(f"Error fetching contract source: {e}")
            return {'error': str(e)}

    def fetch_contract_transactions(self, address: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent transactions for a contract."""
        if not self.api_key:
            return []

        try:
            response = requests.get(
                self.ETHERSCAN_API,
                params={
                    'chainid': self.CHAIN_ID,
                    'module': 'account',
                    'action': 'txlist',
                    'address': address,
                    'startblock': 0,
                    'endblock': 99999999,
                    'page': 1,
                    'offset': limit,
                    'sort': 'desc',
                    'apikey': self.api_key
                },
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1' and data.get('result'):
                    return [
                        {
                            'hash': tx.get('hash'),
                            'from': tx.get('from'),
                            'to': tx.get('to'),
                            'value_eth': int(tx.get('value', 0)) / 1e18,
                            'timestamp': datetime.fromtimestamp(
                                int(tx.get('timeStamp', 0)),
                                tz=timezone.utc
                            ).isoformat(),
                            'block_number': tx.get('blockNumber'),
                            'method_id': tx.get('methodId', ''),
                            'function_name': tx.get('functionName', ''),
                            'is_error': tx.get('isError', '0') == '1',
                        }
                        for tx in data['result']
                    ]

        except Exception as e:
            logger.warning(f"Error fetching contract transactions: {e}")

        return []

    def fetch_contract_events(self, address: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch event logs for a contract."""
        if not self.api_key:
            return []

        try:
            response = requests.get(
                self.ETHERSCAN_API,
                params={
                    'chainid': self.CHAIN_ID,
                    'module': 'logs',
                    'action': 'getLogs',
                    'address': address,
                    'fromBlock': 0,
                    'toBlock': 'latest',
                    'page': 1,
                    'offset': limit,
                    'apikey': self.api_key
                },
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == '1' and data.get('result'):
                    return [
                        {
                            'block_number': int(log.get('blockNumber', '0'), 16),
                            'timestamp': datetime.fromtimestamp(
                                int(log.get('timeStamp', '0'), 16),
                                tz=timezone.utc
                            ).isoformat() if log.get('timeStamp') else None,
                            'tx_hash': log.get('transactionHash'),
                            'topics': log.get('topics', []),
                            'data': log.get('data'),
                        }
                        for log in data['result']
                    ]

        except Exception as e:
            logger.warning(f"Error fetching contract events: {e}")

        return []

    def analyze_contract_risk(self, address: str) -> Dict[str, Any]:
        """
        Analyze contract risk based on transaction patterns and code.

        Returns a risk assessment with:
        - Risk score (0-100)
        - Red flags
        - Transaction analysis
        - Recommendations
        """
        risk_score = 0
        red_flags = []
        analysis = {
            'address': address,
            'risk_score': 0,
            'risk_level': 'LOW',
            'red_flags': [],
            'transaction_analysis': {},
            'recommendations': []
        }

        # Fetch contract info
        contract_info = self.fetch_contract_source(address)

        if contract_info.get('error'):
            analysis['error'] = contract_info['error']
            return analysis

        # Check if verified
        if not contract_info.get('verified'):
            risk_score += 30
            red_flags.append("Contract source code not verified")
            analysis['recommendations'].append("Request source code verification from deployer")

        # Check for proxy pattern
        if contract_info.get('proxy'):
            risk_score += 15
            red_flags.append("Contract uses upgradeable proxy pattern")
            analysis['recommendations'].append("Review implementation contract and upgrade mechanisms")

        # Fetch and analyze transactions
        transactions = self.fetch_contract_transactions(address, limit=100)

        if transactions:
            error_count = sum(1 for tx in transactions if tx.get('is_error'))
            error_rate = error_count / len(transactions)

            if error_rate > 0.1:
                risk_score += 20
                red_flags.append(f"High transaction error rate: {error_rate:.1%}")

            # Check for recent high-value transactions
            recent_value = sum(tx.get('value_eth', 0) for tx in transactions[:10])
            if recent_value > 1000:
                analysis['transaction_analysis']['high_value_activity'] = True
                analysis['recommendations'].append("Monitor for unusual withdrawals")

            analysis['transaction_analysis'] = {
                'total_transactions': len(transactions),
                'error_count': error_count,
                'error_rate': f"{error_rate:.1%}",
                'recent_volume_eth': round(recent_value, 2),
            }

        # Analyze source code if available
        if contract_info.get('source_code'):
            source = contract_info['source_code']

            # Check for dangerous patterns
            dangerous_patterns = {
                'selfdestruct': ('selfdestruct', 25, "Contract contains selfdestruct function"),
                'delegatecall': ('delegatecall', 20, "Contract uses delegatecall"),
                'tx.origin': ('tx.origin', 15, "Contract uses tx.origin for authentication"),
            }

            for pattern_name, (pattern, score, flag) in dangerous_patterns.items():
                if pattern in source.lower():
                    risk_score += score
                    red_flags.append(flag)

        # Calculate final risk level
        analysis['risk_score'] = min(risk_score, 100)

        if risk_score >= 70:
            analysis['risk_level'] = 'CRITICAL'
        elif risk_score >= 50:
            analysis['risk_level'] = 'HIGH'
        elif risk_score >= 30:
            analysis['risk_level'] = 'MEDIUM'
        else:
            analysis['risk_level'] = 'LOW'

        analysis['red_flags'] = red_flags

        if not red_flags:
            analysis['recommendations'].append("No immediate red flags detected - continue standard monitoring")

        return analysis


# Global singleton
_event_listener: Optional[BlockchainEventListener] = None


def get_event_listener() -> BlockchainEventListener:
    """Get or create the global event listener instance."""
    global _event_listener
    if _event_listener is None:
        _event_listener = BlockchainEventListener()
    return _event_listener


def start_blockchain_monitoring() -> None:
    """Start the blockchain event listener."""
    listener = get_event_listener()
    listener.start()


def stop_blockchain_monitoring() -> None:
    """Stop the blockchain event listener."""
    listener = get_event_listener()
    listener.stop()


def audit_contract_by_address(address: str) -> Dict[str, Any]:
    """
    Audit a smart contract by its address.

    This function:
    1. Fetches the contract source code from Etherscan
    2. Analyzes transaction patterns
    3. Runs the SmartContractAuditorAgent on the code
    4. Returns a comprehensive audit report
    """
    listener = get_event_listener()

    # Step 1: Fetch contract info
    contract_info = listener.fetch_contract_source(address)

    if contract_info.get('error'):
        return {
            'success': False,
            'address': address,
            'error': contract_info['error']
        }

    if not contract_info.get('verified'):
        return {
            'success': False,
            'address': address,
            'error': 'Contract not verified on Etherscan - cannot audit unverified code',
            'recommendation': 'Request the deployer to verify the contract on Etherscan'
        }

    # Step 2: Risk analysis
    risk_analysis = listener.analyze_contract_risk(address)

    # Step 3: Run SmartContractAuditorAgent on the code
    try:
        from core.agents.blockchain import SmartContractAuditorAgent

        auditor = SmartContractAuditorAgent()

        # Prepare source code (handle Solidity Standard JSON)
        source_code = contract_info.get('source_code', '')
        if source_code.startswith('{{'):
            # Multiple files in JSON format.
            # Session 1103c: was 'except Exception: pass  # Use as-is
            # if parsing fails' which silently fed the raw double-
            # brace-wrapped JSON into the smart-contract auditor on
            # any json.loads failure. The auditor would then either
            # fail later or audit garbage, with no trail explaining
            # the parse failure. Now logs at warning so we know when
            # an Etherscan response shape needs investigation.
            import json
            try:
                sources = json.loads(source_code[1:-1])  # Remove extra braces
                source_code = "\n\n".join(
                    f"// File: {name}\n{src.get('content', '')}"
                    for name, src in sources.get('sources', {}).items()
                )
            except Exception as e:
                logger.warning(
                    "blockchain_event_listener: multi-file source JSON "
                    "parse failed for contract %s (%s: %s) — feeding "
                    "raw wrapped source to auditor, audit may be "
                    "garbled",
                    address, type(e).__name__, e,
                )

        audit_result = auditor.execute(
            task=f"Audit this smart contract at address {address}:\n\n{source_code}",
            context={'address': address, 'contract_name': contract_info.get('contract_name')},
            scifi_context={},
            spider_context={}
        )

        return {
            'success': True,
            'address': address,
            'contract_name': contract_info.get('contract_name'),
            'compiler_version': contract_info.get('compiler_version'),
            'is_proxy': contract_info.get('proxy', False),
            'risk_analysis': risk_analysis,
            'audit_result': {
                'success': audit_result.success,
                'message': audit_result.message,
                'data': audit_result.data if hasattr(audit_result, 'data') else {},
            },
            'transaction_count': risk_analysis.get('transaction_analysis', {}).get('total_transactions', 0),
            'etherscan_link': f"https://etherscan.io/address/{address}"
        }

    except Exception as e:
        logger.error(f"Contract audit failed: {e}")
        return {
            'success': False,
            'address': address,
            'error': f"Audit failed: {str(e)}",
            'risk_analysis': risk_analysis
        }
