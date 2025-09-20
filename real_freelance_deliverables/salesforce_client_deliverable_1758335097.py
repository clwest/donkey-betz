#!/usr/bin/env python3
"""
Salesforce CRM Integration Client
Client: TechStart Innovations
Agent: CodeMaster-7
Platform: Fiverr

REAL DELIVERABLE - Production CRM Integration
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import time
import urllib.parse
from pathlib import Path
import csv

@dataclass
class Contact:
    """Salesforce Contact record"""
    FirstName: str
    LastName: str
    Email: str
    Phone: Optional[str] = None
    AccountId: Optional[str] = None
    Title: Optional[str] = None
    Department: Optional[str] = None
    LeadSource: Optional[str] = None
    Id: Optional[str] = None

@dataclass
class Account:
    """Salesforce Account record"""
    Name: str
    Type: Optional[str] = None
    Industry: Optional[str] = None
    Phone: Optional[str] = None
    Website: Optional[str] = None
    BillingStreet: Optional[str] = None
    BillingCity: Optional[str] = None
    BillingState: Optional[str] = None
    BillingPostalCode: Optional[str] = None
    NumberOfEmployees: Optional[int] = None
    AnnualRevenue: Optional[float] = None
    Id: Optional[str] = None

class SalesforceClient:
    """
    Production-ready Salesforce REST API client
    Features:
    - OAuth2 authentication with token refresh
    - Full CRUD operations for standard objects
    - Bulk data operations with batching
    - Comprehensive error handling and logging
    - Rate limiting and retry logic
    - Data validation and sanitization
    """

    def __init__(self, client_id: str, client_secret: str, username: str,
                 password: str, security_token: str, sandbox: bool = False):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.security_token = security_token
        self.sandbox = sandbox

        # API configuration
        self.login_url = "https://test.salesforce.com" if sandbox else "https://login.salesforce.com"
        self.api_version = "v58.0"

        # Session management
        self.access_token = None
        self.instance_url = None
        self.session_expires = None
        self.refresh_token = None

        # HTTP session for connection pooling
        self.session = requests.Session()
        self.session.timeout = 30

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        self.daily_api_calls = 0
        self.daily_limit = 15000  # Conservative daily limit

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('salesforce_client.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def authenticate(self) -> bool:
        """
        Authenticate with Salesforce using OAuth2 username-password flow

        Returns:
            bool: Success status
        """
        try:
            self.logger.info("Authenticating with Salesforce...")

            token_url = f"{self.login_url}/services/oauth2/token"

            payload = {
                'grant_type': 'password',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'username': self.username,
                'password': f"{self.password}{self.security_token}"
            }

            response = self.session.post(token_url, data=payload)

            if response.status_code == 200:
                auth_data = response.json()

                self.access_token = auth_data['access_token']
                self.instance_url = auth_data['instance_url']
                self.session_expires = datetime.now() + timedelta(seconds=3600)  # 1 hour default

                # Update session headers
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                })

                self.logger.info(f"Successfully authenticated with {self.instance_url}")
                return True
            else:
                self.logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False

    def _ensure_authenticated(self) -> bool:
        """Ensure valid authentication token"""
        if not self.access_token or (self.session_expires and datetime.now() >= self.session_expires):
            return self.authenticate()
        return True

    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)

        self.last_request_time = time.time()
        self.daily_api_calls += 1

        if self.daily_api_calls >= self.daily_limit:
            self.logger.warning("Approaching daily API limit")

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                     params: Optional[Dict] = None, retry_count: int = 0) -> Optional[Dict]:
        """
        Make authenticated API request with comprehensive error handling

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request payload
            params: Query parameters
            retry_count: Current retry attempt

        Returns:
            API response or None on failure
        """
        if not self._ensure_authenticated():
            return None

        self._rate_limit()

        url = f"{self.instance_url}/services/data/{self.api_version}/{endpoint}"

        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params)
            elif method.upper() == 'PATCH':
                response = self.session.patch(url, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params)
            else:
                self.logger.error(f"Unsupported HTTP method: {method}")
                return None

            # Handle response codes
            if response.status_code in [200, 201]:
                return response.json() if response.text else {"success": True}
            elif response.status_code == 204:
                return {"success": True}
            elif response.status_code == 401 and retry_count < 1:
                # Token expired, re-authenticate and retry
                self.logger.warning("Token expired, re-authenticating...")
                if self.authenticate():
                    return self._make_request(method, endpoint, data, params, retry_count + 1)
                return None
            elif response.status_code == 429:
                # Rate limited
                retry_after = int(response.headers.get('Retry-After', 5))
                self.logger.warning(f"Rate limited, waiting {retry_after} seconds")
                time.sleep(retry_after)
                if retry_count < 3:
                    return self._make_request(method, endpoint, data, params, retry_count + 1)
                return None
            else:
                self.logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None

        except requests.RequestException as e:
            self.logger.error(f"Request error: {e}")
            if retry_count < 2:
                time.sleep(2 ** retry_count)  # Exponential backoff
                return self._make_request(method, endpoint, data, params, retry_count + 1)
            return None

    # Contact Operations
    def create_contact(self, contact: Contact) -> Optional[str]:
        """
        Create a new contact in Salesforce

        Args:
            contact: Contact object

        Returns:
            Contact ID if successful, None otherwise
        """
        contact_data = self._sanitize_data(asdict(contact))
        contact_data = {k: v for k, v in contact_data.items() if v is not None and k != 'Id'}

        # Validate required fields
        if not contact_data.get('LastName') or not contact_data.get('Email'):
            self.logger.error("Contact must have LastName and Email")
            return None

        result = self._make_request('POST', 'sobjects/Contact/', data=contact_data)

        if result and result.get('success'):
            contact_id = result.get('id')
            self.logger.info(f"Created contact: {contact_id} ({contact.Email})")
            return contact_id
        else:
            self.logger.error(f"Failed to create contact: {contact.Email}")
            return None

    def get_contact(self, contact_id: str, fields: Optional[List[str]] = None) -> Optional[Contact]:
        """
        Retrieve a contact by ID

        Args:
            contact_id: Salesforce contact ID
            fields: List of fields to retrieve

        Returns:
            Contact object or None
        """
        if fields:
            field_list = ','.join(fields)
            params = {'fields': field_list}
        else:
            params = None

        result = self._make_request('GET', f'sobjects/Contact/{contact_id}', params=params)

        if result:
            return Contact(
                Id=result.get('Id'),
                FirstName=result.get('FirstName', ''),
                LastName=result.get('LastName', ''),
                Email=result.get('Email', ''),
                Phone=result.get('Phone'),
                AccountId=result.get('AccountId'),
                Title=result.get('Title'),
                Department=result.get('Department'),
                LeadSource=result.get('LeadSource')
            )
        return None

    def update_contact(self, contact_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing contact

        Args:
            contact_id: Salesforce contact ID
            updates: Dictionary of field updates

        Returns:
            Success status
        """
        sanitized_updates = self._sanitize_data(updates)

        result = self._make_request('PATCH', f'sobjects/Contact/{contact_id}', data=sanitized_updates)

        if result and result.get('success'):
            self.logger.info(f"Updated contact: {contact_id}")
            return True
        else:
            self.logger.error(f"Failed to update contact: {contact_id}")
            return False

    def delete_contact(self, contact_id: str) -> bool:
        """Delete a contact"""
        result = self._make_request('DELETE', f'sobjects/Contact/{contact_id}')

        if result and result.get('success'):
            self.logger.info(f"Deleted contact: {contact_id}")
            return True
        else:
            self.logger.error(f"Failed to delete contact: {contact_id}")
            return False

    def search_contacts(self, search_criteria: Dict[str, Any], limit: int = 100) -> List[Contact]:
        """
        Search for contacts using SOQL

        Args:
            search_criteria: Dictionary of search criteria
            limit: Maximum number of results

        Returns:
            List of Contact objects
        """
        conditions = []

        for field, value in search_criteria.items():
            if value:
                if field in ['Email']:
                    conditions.append(f"{field} = '{value}'")
                elif field in ['FirstName', 'LastName']:
                    conditions.append(f"{field} LIKE '%{value}%'")
                else:
                    conditions.append(f"{field} = '{value}'")

        if not conditions:
            self.logger.error("No search criteria provided")
            return []

        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT Id, FirstName, LastName, Email, Phone, AccountId, Title, Department, LeadSource
            FROM Contact
            WHERE {where_clause}
            LIMIT {limit}
        """

        result = self._make_request('GET', 'query/', params={'q': query})

        contacts = []
        if result and result.get('records'):
            for record in result['records']:
                contacts.append(Contact(
                    Id=record.get('Id'),
                    FirstName=record.get('FirstName', ''),
                    LastName=record.get('LastName', ''),
                    Email=record.get('Email', ''),
                    Phone=record.get('Phone'),
                    AccountId=record.get('AccountId'),
                    Title=record.get('Title'),
                    Department=record.get('Department'),
                    LeadSource=record.get('LeadSource')
                ))

        return contacts

    # Account Operations
    def create_account(self, account: Account) -> Optional[str]:
        """Create a new account"""
        account_data = self._sanitize_data(asdict(account))
        account_data = {k: v for k, v in account_data.items() if v is not None and k != 'Id'}

        if not account_data.get('Name'):
            self.logger.error("Account must have a Name")
            return None

        result = self._make_request('POST', 'sobjects/Account/', data=account_data)

        if result and result.get('success'):
            account_id = result.get('id')
            self.logger.info(f"Created account: {account_id} ({account.Name})")
            return account_id
        else:
            self.logger.error(f"Failed to create account: {account.Name}")
            return None

    def get_account(self, account_id: str) -> Optional[Account]:
        """Retrieve an account by ID"""
        result = self._make_request('GET', f'sobjects/Account/{account_id}')

        if result:
            return Account(
                Id=result.get('Id'),
                Name=result.get('Name', ''),
                Type=result.get('Type'),
                Industry=result.get('Industry'),
                Phone=result.get('Phone'),
                Website=result.get('Website'),
                BillingStreet=result.get('BillingStreet'),
                BillingCity=result.get('BillingCity'),
                BillingState=result.get('BillingState'),
                BillingPostalCode=result.get('BillingPostalCode'),
                NumberOfEmployees=result.get('NumberOfEmployees'),
                AnnualRevenue=result.get('AnnualRevenue')
            )
        return None

    # Bulk Operations
    def bulk_create_contacts(self, contacts: List[Contact], batch_size: int = 200) -> Dict[str, Any]:
        """
        Create multiple contacts in batches

        Args:
            contacts: List of Contact objects
            batch_size: Number of records per batch

        Returns:
            Results summary
        """
        results = {
            'total_contacts': len(contacts),
            'successful_creates': 0,
            'failed_creates': 0,
            'errors': [],
            'created_ids': []
        }

        # Process in batches
        for i in range(0, len(contacts), batch_size):
            batch = contacts[i:i + batch_size]
            batch_results = self._process_contact_batch(batch, 'create')

            results['successful_creates'] += batch_results['successful']
            results['failed_creates'] += batch_results['failed']
            results['errors'].extend(batch_results['errors'])
            results['created_ids'].extend(batch_results['ids'])

            # Rate limiting between batches
            if i + batch_size < len(contacts):
                time.sleep(1)

        self.logger.info(f"Bulk create completed: {results['successful_creates']}/{results['total_contacts']} successful")
        return results

    def _process_contact_batch(self, contacts: List[Contact], operation: str) -> Dict[str, Any]:
        """Process a batch of contacts"""
        batch_results = {
            'successful': 0,
            'failed': 0,
            'errors': [],
            'ids': []
        }

        for contact in contacts:
            try:
                if operation == 'create':
                    contact_id = self.create_contact(contact)
                    if contact_id:
                        batch_results['successful'] += 1
                        batch_results['ids'].append(contact_id)
                    else:
                        batch_results['failed'] += 1
                        batch_results['errors'].append(f"Failed to create: {contact.Email}")
            except Exception as e:
                batch_results['failed'] += 1
                batch_results['errors'].append(f"Error processing {contact.Email}: {str(e)}")

        return batch_results

    def sync_customer_data(self, customer_file: str) -> Dict[str, Any]:
        """
        Sync customer data from CSV file

        Args:
            customer_file: Path to CSV file with customer data

        Returns:
            Sync results
        """
        results = {
            'status': 'started',
            'file': customer_file,
            'accounts_created': 0,
            'contacts_created': 0,
            'errors': [],
            'processing_time': 0
        }

        start_time = time.time()

        try:
            # Read customer data
            customers = []
            with open(customer_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                customers = list(reader)

            self.logger.info(f"Processing {len(customers)} customer records from {customer_file}")

            for customer in customers:
                try:
                    # Create account
                    account = Account(
                        Name=customer.get('company_name', f"{customer.get('first_name', '')} {customer.get('last_name', '')}").strip(),
                        Type=customer.get('account_type', 'Customer'),
                        Industry=customer.get('industry'),
                        Phone=customer.get('company_phone'),
                        Website=customer.get('website'),
                        BillingStreet=customer.get('address'),
                        BillingCity=customer.get('city'),
                        BillingState=customer.get('state'),
                        BillingPostalCode=customer.get('zip_code')
                    )

                    account_id = self.create_account(account)
                    if account_id:
                        results['accounts_created'] += 1

                        # Create contact linked to account
                        contact = Contact(
                            FirstName=customer.get('first_name', ''),
                            LastName=customer.get('last_name', ''),
                            Email=customer.get('email', ''),
                            Phone=customer.get('phone'),
                            AccountId=account_id,
                            Title=customer.get('title'),
                            Department=customer.get('department'),
                            LeadSource=customer.get('lead_source', 'Import')
                        )

                        contact_id = self.create_contact(contact)
                        if contact_id:
                            results['contacts_created'] += 1
                        else:
                            results['errors'].append(f"Failed to create contact for {customer.get('email')}")
                    else:
                        results['errors'].append(f"Failed to create account for {customer.get('company_name')}")

                except Exception as e:
                    results['errors'].append(f"Error processing customer {customer.get('email', 'unknown')}: {str(e)}")

            results['processing_time'] = time.time() - start_time
            results['status'] = 'completed'

        except Exception as e:
            results['status'] = 'error'
            results['errors'].append(f"File processing error: {str(e)}")

        return results

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data for Salesforce API"""
        sanitized = {}

        for key, value in data.items():
            if value is not None:
                if isinstance(value, str):
                    # Trim whitespace and handle empty strings
                    cleaned_value = value.strip()
                    if cleaned_value:
                        sanitized[key] = cleaned_value
                else:
                    sanitized[key] = value

        return sanitized

    def get_api_usage(self) -> Dict[str, Any]:
        """Get current API usage statistics"""
        return {
            'daily_calls_made': self.daily_api_calls,
            'daily_limit': self.daily_limit,
            'remaining_calls': self.daily_limit - self.daily_api_calls,
            'percentage_used': (self.daily_api_calls / self.daily_limit) * 100
        }

def main():
    """Demonstration of Salesforce client capabilities"""
    # Configuration (replace with actual credentials)
    config = {
        'client_id': 'your_salesforce_client_id',
        'client_secret': 'your_salesforce_client_secret',
        'username': 'your_salesforce_username@company.com',
        'password': 'your_salesforce_password',
        'security_token': 'your_salesforce_security_token',
        'sandbox': True  # Set to False for production
    }

    # Initialize client
    client = SalesforceClient(**config)

    # Authenticate
    print("Connecting to Salesforce...")
    if not client.authenticate():
        print("❌ Authentication failed!")
        print("Please check your credentials and try again.")
        return

    print("✅ Successfully connected to Salesforce!")

    # Demonstrate account creation
    print("\n=== Creating Sample Account ===")
    sample_account = Account(
        Name="TechStart Innovations Demo",
        Type="Customer",
        Industry="Technology",
        Phone="(555) 123-4567",
        Website="https://techstart-demo.com",
        BillingStreet="123 Innovation Drive",
        BillingCity="San Francisco",
        BillingState="CA",
        BillingPostalCode="94107",
        NumberOfEmployees=50,
        AnnualRevenue=5000000.0
    )

    account_id = client.create_account(sample_account)
    if account_id:
        print(f"✅ Created account: {account_id}")

        # Create contacts for the account
        print("\n=== Creating Sample Contacts ===")
        sample_contacts = [
            Contact(
                FirstName="John",
                LastName="Smith",
                Email="john.smith@techstart-demo.com",
                Phone="(555) 123-4568",
                AccountId=account_id,
                Title="CEO",
                Department="Executive",
                LeadSource="Website"
            ),
            Contact(
                FirstName="Sarah",
                LastName="Johnson",
                Email="sarah.johnson@techstart-demo.com",
                Phone="(555) 123-4569",
                AccountId=account_id,
                Title="CTO",
                Department="Technology",
                LeadSource="Referral"
            )
        ]

        for contact in sample_contacts:
            contact_id = client.create_contact(contact)
            if contact_id:
                print(f"✅ Created contact: {contact.FirstName} {contact.LastName} ({contact_id})")

        # Demonstrate search
        print("\n=== Searching Contacts ===")
        search_results = client.search_contacts({'AccountId': account_id})
        print(f"Found {len(search_results)} contacts for account")

        for contact in search_results:
            print(f"  • {contact.FirstName} {contact.LastName} - {contact.Title}")

    # Display API usage
    usage = client.get_api_usage()
    print(f"\n=== API Usage ===")
    print(f"Calls made today: {usage['daily_calls_made']}")
    print(f"Daily limit: {usage['daily_limit']}")
    print(f"Usage: {usage['percentage_used']:.1f}%")

    # Create sample CSV for bulk import demo
    sample_csv_file = "sample_customers.csv"
    sample_data = [
        {
            'first_name': 'Alice',
            'last_name': 'Williams',
            'email': 'alice@example-corp.com',
            'phone': '(555) 200-0001',
            'company_name': 'Example Corp',
            'title': 'Marketing Director',
            'industry': 'Marketing',
            'lead_source': 'Trade Show'
        },
        {
            'first_name': 'Bob',
            'last_name': 'Davis',
            'email': 'bob@demo-solutions.com',
            'phone': '(555) 200-0002',
            'company_name': 'Demo Solutions Inc',
            'title': 'Sales Manager',
            'industry': 'Software',
            'lead_source': 'Cold Call'
        }
    ]

    # Write sample CSV
    with open(sample_csv_file, 'w', newline='', encoding='utf-8') as f:
        if sample_data:
            writer = csv.DictWriter(f, fieldnames=sample_data[0].keys())
            writer.writeheader()
            writer.writerows(sample_data)

    print(f"\n=== Bulk Import Demo ===")
    print(f"Created sample file: {sample_csv_file}")

    # Demonstrate bulk sync (commented out for demo)
    # sync_results = client.sync_customer_data(sample_csv_file)
    # print(f"Sync results: {sync_results}")

    return {
        'status': 'success',
        'account_created': account_id is not None,
        'contacts_created': len(sample_contacts),
        'api_calls_used': usage['daily_calls_made']
    }

if __name__ == "__main__":
    result = main()
    print(f"\nDemo completed with status: {result['status']}")
