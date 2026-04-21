#!/usr/bin/env python3
"""
Excel Data Processing Automation
Client: SalesForce Solutions
Agent: DataWizard-9
Platform: Freelancer.com

REAL DELIVERABLE - Weekly Sales Report Automation
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import glob
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.charts import BarChart, LineChart, Reference
import warnings
warnings.filterwarnings('ignore')

class WeeklySalesProcessor:
    """
    Professional Excel data processing automation
    Features:
    - Automated file discovery and processing
    - Data validation and cleaning
    - Statistical analysis and reporting
    - Executive summary generation
    - Formatted Excel output with charts
    """

    def __init__(self, input_dir: str = "weekly_reports", output_dir: str = "processed_reports"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)

        # Create directories
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / 'processing.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Processing statistics
        self.stats = {
            'files_processed': 0,
            'total_records': 0,
            'errors': [],
            'processing_time': 0
        }

    def process_weekly_reports(self) -> Dict[str, Any]:
        """
        Main processing function - processes all Excel files in input directory

        Returns:
            Processing results and statistics
        """
        start_time = datetime.now()
        self.logger.info(f"Starting weekly sales report processing at {start_time}")

        # Find all Excel files
        excel_files = self._find_excel_files()
        if not excel_files:
            return self._create_error_result("No Excel files found in input directory")

        self.logger.info(f"Found {len(excel_files)} Excel files to process")

        # Process each file
        all_data = []
        file_results = []

        for file_path in excel_files:
            try:
                self.logger.info(f"Processing {file_path.name}...")
                file_data, file_result = self._process_single_file(file_path)

                if file_data:
                    all_data.extend(file_data)
                    file_results.append(file_result)
                    self.stats['files_processed'] += 1
                    self.stats['total_records'] += len(file_data)
                else:
                    self.stats['errors'].append(f"No data extracted from {file_path.name}")

            except Exception as e:
                error_msg = f"Error processing {file_path.name}: {str(e)}"
                self.logger.error(error_msg)
                self.stats['errors'].append(error_msg)

        if not all_data:
            return self._create_error_result("No data could be processed from any files")

        # Create master dataset
        df = pd.DataFrame(all_data)
        self.logger.info(f"Created master dataset with {len(df)} records")

        # Process and analyze data
        processed_df = self._clean_and_process_data(df)
        analysis_results = self._perform_analysis(processed_df)

        # Generate outputs
        output_files = self._generate_outputs(processed_df, analysis_results)

        # Calculate processing time
        end_time = datetime.now()
        self.stats['processing_time'] = (end_time - start_time).total_seconds()

        return {
            'status': 'success',
            'processing_time': self.stats['processing_time'],
            'files_processed': self.stats['files_processed'],
            'total_records': self.stats['total_records'],
            'errors': self.stats['errors'],
            'file_results': file_results,
            'analysis': analysis_results,
            'output_files': output_files,
            'summary': self._create_executive_summary(processed_df, analysis_results)
        }

    def _find_excel_files(self) -> List[Path]:
        """Find all Excel files in input directory"""
        patterns = ['*.xlsx', '*.xls', '*.xlsm']
        files = []

        for pattern in patterns:
            files.extend(self.input_dir.glob(pattern))

        return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)

    def _process_single_file(self, file_path: Path) -> tuple:
        """Process a single Excel file"""
        try:
            # Read all sheets to find data
            excel_file = pd.ExcelFile(file_path)

            all_sheet_data = []
            sheets_processed = []

            for sheet_name in excel_file.sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)

                    if len(df) > 0 and self._is_sales_data(df):
                        df = self._standardize_columns(df)
                        df['source_file'] = file_path.name
                        df['source_sheet'] = sheet_name
                        df['processed_timestamp'] = datetime.now()

                        all_sheet_data.extend(df.to_dict('records'))
                        sheets_processed.append(sheet_name)

                except Exception as e:
                    self.logger.warning(f"Could not process sheet '{sheet_name}' in {file_path.name}: {e}")

            file_result = {
                'file': file_path.name,
                'sheets_processed': sheets_processed,
                'records_extracted': len(all_sheet_data),
                'status': 'success' if all_sheet_data else 'no_data'
            }

            return all_sheet_data, file_result

        except Exception as e:
            self.logger.error(f"Error reading {file_path.name}: {e}")
            return [], {'file': file_path.name, 'status': 'error', 'error': str(e)}

    def _is_sales_data(self, df: pd.DataFrame) -> bool:
        """Check if DataFrame contains sales data"""
        sales_indicators = [
            'sale', 'revenue', 'amount', 'total', 'price', 'value',
            'customer', 'client', 'product', 'item', 'date', 'order'
        ]

        column_text = ' '.join(df.columns.astype(str)).lower()
        return any(indicator in column_text for indicator in sales_indicators)

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names across different file formats"""
        # Clean column names
        df.columns = df.columns.astype(str).str.strip().str.lower()
        df.columns = df.columns.str.replace(' ', '_').str.replace('-', '_')

        # Column mapping dictionary
        column_mappings = {
            'date': ['date', 'sale_date', 'order_date', 'transaction_date', 'invoice_date'],
            'amount': ['amount', 'total', 'revenue', 'sales', 'value', 'price', 'sum'],
            'product': ['product', 'item', 'product_name', 'item_name', 'service'],
            'customer': ['customer', 'client', 'customer_name', 'buyer', 'account'],
            'salesperson': ['salesperson', 'rep', 'sales_rep', 'representative', 'agent'],
            'region': ['region', 'territory', 'area', 'location', 'state', 'city'],
            'category': ['category', 'type', 'department', 'division', 'segment'],
            'quantity': ['quantity', 'qty', 'units', 'count', 'volume']
        }

        # Apply mappings
        for standard_col, possible_cols in column_mappings.items():
            for col in df.columns:
                if col in possible_cols:
                    df = df.rename(columns={col: standard_col})
                    break

        return df

    def _clean_and_process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and process the combined dataset"""
        self.logger.info("Cleaning and processing data...")

        # Remove completely empty rows
        df = df.dropna(how='all')

        # Handle date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])

            # Add date components for analysis
            df['year'] = df['date'].dt.year
            df['month'] = df['date'].dt.month
            df['quarter'] = df['date'].dt.quarter
            df['week'] = df['date'].dt.isocalendar().week
            df['day_of_week'] = df['date'].dt.day_name()
            df['month_name'] = df['date'].dt.month_name()

        # Handle amount column
        if 'amount' in df.columns:
            # Convert to numeric, handle currency symbols
            df['amount'] = df['amount'].astype(str).str.replace(r'[$,]', '', regex=True)
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            df = df.dropna(subset=['amount'])
            df = df[df['amount'] > 0]  # Remove negative and zero amounts

        # Handle quantity
        if 'quantity' in df.columns:
            df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
            df['quantity'] = df['quantity'].fillna(1)  # Default to 1 if missing

        # Fill missing categorical data
        categorical_columns = ['product', 'customer', 'salesperson', 'region', 'category']
        for col in categorical_columns:
            if col in df.columns:
                df[col] = df[col].fillna('Unknown')
                df[col] = df[col].astype(str).str.strip()

        # Remove duplicates
        df = df.drop_duplicates()

        self.logger.info(f"Data cleaning completed. Final dataset: {len(df)} records")
        return df

    def _perform_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform comprehensive sales analysis"""
        self.logger.info("Performing sales analysis...")

        analysis = {
            'overview': self._calculate_overview_stats(df),
            'trends': self._analyze_trends(df),
            'performance': self._analyze_performance(df),
            'insights': self._generate_insights(df)
        }

        return analysis

    def _calculate_overview_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate overview statistics"""
        stats = {
            'total_records': len(df),
            'date_range': {
                'start': df['date'].min().strftime('%Y-%m-%d') if 'date' in df.columns else None,
                'end': df['date'].max().strftime('%Y-%m-%d') if 'date' in df.columns else None
            }
        }

        if 'amount' in df.columns:
            stats.update({
                'total_revenue': float(df['amount'].sum()),
                'average_sale': float(df['amount'].mean()),
                'median_sale': float(df['amount'].median()),
                'largest_sale': float(df['amount'].max()),
                'smallest_sale': float(df['amount'].min())
            })

        return stats

    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze sales trends"""
        trends = {}

        if 'date' in df.columns and 'amount' in df.columns:
            # Daily trends
            daily_sales = df.groupby('date')['amount'].agg(['sum', 'count', 'mean'])
            trends['daily'] = {
                'best_day': {
                    'date': daily_sales['sum'].idxmax().strftime('%Y-%m-%d'),
                    'revenue': float(daily_sales['sum'].max())
                },
                'average_daily_revenue': float(daily_sales['sum'].mean())
            }

            # Monthly trends
            if 'month_name' in df.columns:
                monthly_sales = df.groupby('month_name')['amount'].agg(['sum', 'count', 'mean'])
                trends['monthly'] = monthly_sales.to_dict()

            # Weekly trends
            if 'day_of_week' in df.columns:
                weekly_pattern = df.groupby('day_of_week')['amount'].agg(['sum', 'count', 'mean'])
                trends['weekly_pattern'] = weekly_pattern.to_dict()

        return trends

    def _analyze_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance by different dimensions"""
        performance = {}

        if 'amount' in df.columns:
            # Product performance
            if 'product' in df.columns:
                product_perf = df.groupby('product')['amount'].agg(['sum', 'count', 'mean']).round(2)
                performance['top_products'] = product_perf.nlargest(10, 'sum').to_dict()

            # Customer performance
            if 'customer' in df.columns:
                customer_perf = df.groupby('customer')['amount'].agg(['sum', 'count', 'mean']).round(2)
                performance['top_customers'] = customer_perf.nlargest(10, 'sum').to_dict()

            # Salesperson performance
            if 'salesperson' in df.columns:
                sales_perf = df.groupby('salesperson')['amount'].agg(['sum', 'count', 'mean']).round(2)
                performance['top_salespeople'] = sales_perf.nlargest(10, 'sum').to_dict()

            # Regional performance
            if 'region' in df.columns:
                region_perf = df.groupby('region')['amount'].agg(['sum', 'count', 'mean']).round(2)
                performance['regional'] = region_perf.to_dict()

        return performance

    def _generate_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate business insights"""
        insights = []

        if 'amount' in df.columns:
            total_revenue = df['amount'].sum()
            avg_sale = df['amount'].mean()

            insights.append(f"Total revenue: ${total_revenue:,.2f}")
            insights.append(f"Average sale amount: ${avg_sale:,.2f}")

            if 'date' in df.columns:
                days_in_period = (df['date'].max() - df['date'].min()).days + 1
                daily_avg = total_revenue / days_in_period
                insights.append(f"Average daily revenue: ${daily_avg:,.2f}")

                # Growth analysis
                if days_in_period > 7:
                    first_week = df[df['date'] <= df['date'].min() + timedelta(days=7)]['amount'].sum()
                    last_week = df[df['date'] >= df['date'].max() - timedelta(days=7)]['amount'].sum()

                    if first_week > 0:
                        growth = ((last_week - first_week) / first_week) * 100
                        trend = "increasing" if growth > 0 else "decreasing"
                        insights.append(f"Revenue is {trend} ({growth:+.1f}% week-over-week)")

        return insights

    def _generate_outputs(self, df: pd.DataFrame, analysis: Dict[str, Any]) -> List[str]:
        """Generate output files"""
        output_files = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Excel report with multiple sheets and formatting
        excel_file = self.output_dir / f'weekly_sales_report_{timestamp}.xlsx'
        self._create_formatted_excel_report(df, analysis, excel_file)
        output_files.append(str(excel_file))

        # JSON analysis file
        json_file = self.output_dir / f'sales_analysis_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        output_files.append(str(json_file))

        # CSV data export
        csv_file = self.output_dir / f'processed_sales_data_{timestamp}.csv'
        df.to_csv(csv_file, index=False)
        output_files.append(str(csv_file))

        return output_files

    def _create_formatted_excel_report(self, df: pd.DataFrame, analysis: Dict, filename: Path):
        """Create professionally formatted Excel report"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name='Sales_Data', index=False)

            # Summary sheet
            summary_data = []
            if 'overview' in analysis:
                for key, value in analysis['overview'].items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            summary_data.append({'Metric': f'{key}_{sub_key}', 'Value': sub_value})
                    else:
                        summary_data.append({'Metric': key, 'Value': value})

            if summary_data:
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

            # Performance sheets
            if 'performance' in analysis:
                perf = analysis['performance']

                if 'top_products' in perf:
                    prod_df = pd.DataFrame(perf['top_products']).T
                    prod_df.to_excel(writer, sheet_name='Top_Products')

                if 'top_customers' in perf:
                    cust_df = pd.DataFrame(perf['top_customers']).T
                    cust_df.to_excel(writer, sheet_name='Top_Customers')

                if 'top_salespeople' in perf:
                    sales_df = pd.DataFrame(perf['top_salespeople']).T
                    sales_df.to_excel(writer, sheet_name='Sales_Performance')

        self.logger.info(f"Created formatted Excel report: {filename}")

    def _create_executive_summary(self, df: pd.DataFrame, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary"""
        return {
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_period': analysis.get('overview', {}).get('date_range', {}),
            'key_metrics': analysis.get('overview', {}),
            'top_insights': analysis.get('insights', []),
            'files_processed': self.stats['files_processed'],
            'total_records': self.stats['total_records'],
            'processing_time_seconds': self.stats['processing_time'],
            'recommendation': 'Review top performing products and salespeople for best practices'
        }

    def _create_error_result(self, message: str) -> Dict[str, Any]:
        """Create error result structure"""
        return {
            'status': 'error',
            'message': message,
            'processing_time': 0,
            'files_processed': 0,
            'total_records': 0,
            'errors': [message]
        }

    def create_sample_data(self, num_files: int = 3, records_per_file: int = 50):
        """Create sample Excel files for testing"""
        self.logger.info(f"Creating {num_files} sample Excel files...")

        for file_num in range(num_files):
            # Generate realistic sample data
            data = []
            start_date = datetime.now() - timedelta(days=30)

            for i in range(records_per_file):
                sale_date = start_date + timedelta(days=np.random.randint(0, 30))

                data.append({
                    'Date': sale_date.strftime('%Y-%m-%d'),
                    'Amount': round(np.random.uniform(25, 2500), 2),
                    'Product': np.random.choice([
                        'Software License', 'Consulting Service', 'Training Package',
                        'Support Contract', 'Custom Development', 'Data Analysis'
                    ]),
                    'Customer': f'Customer_{np.random.randint(1, 25)}',
                    'Salesperson': np.random.choice([
                        'Alice Johnson', 'Bob Smith', 'Carol Wilson',
                        'David Brown', 'Eve Davis', 'Frank Miller'
                    ]),
                    'Region': np.random.choice(['North', 'South', 'East', 'West', 'Central']),
                    'Category': np.random.choice(['Software', 'Services', 'Training', 'Support']),
                    'Quantity': np.random.randint(1, 10)
                })

            # Save to Excel
            df = pd.DataFrame(data)
            filename = self.input_dir / f'sales_week_{file_num + 1}.xlsx'
            df.to_excel(filename, index=False, sheet_name='Sales_Data')

        self.logger.info(f"Sample files created in {self.input_dir}")

def main():
    """Main execution function"""
    processor = WeeklySalesProcessor()

    # Create sample data for demonstration
    print("Creating sample sales data...")
    processor.create_sample_data(num_files=3, records_per_file=75)

    # Process the reports
    print("\nProcessing weekly sales reports...")
    results = processor.process_weekly_reports()

    # Display results
    print(f"\n=== PROCESSING COMPLETED ===")
    print(f"Status: {results['status']}")
    print(f"Files processed: {results['files_processed']}")
    print(f"Total records: {results['total_records']}")
    print(f"Processing time: {results['processing_time']:.2f} seconds")

    if results['status'] == 'success':
        summary = results['summary']
        print(f"\n=== EXECUTIVE SUMMARY ===")
        print(f"Report period: {summary['data_period']['start']} to {summary['data_period']['end']}")
        print(f"Total revenue: ${summary['key_metrics']['total_revenue']:,.2f}")
        print(f"Average sale: ${summary['key_metrics']['average_sale']:,.2f}")
        print(f"Number of transactions: {summary['key_metrics']['total_records']}")

        print(f"\n=== KEY INSIGHTS ===")
        for insight in summary['top_insights']:
            print(f"• {insight}")

        print(f"\n=== OUTPUT FILES ===")
        for file_path in results['output_files']:
            print(f"• {Path(file_path).name}")

    if results.get('errors'):
        print(f"\n=== ERRORS ===")
        for error in results['errors']:
            print(f"• {error}")

    return results

if __name__ == "__main__":
    result = main()
    print(f"\nExecution completed with status: {result['status']}")
