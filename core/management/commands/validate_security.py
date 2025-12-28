"""
Management command to validate platform security configuration
"""

from django.core.management.base import BaseCommand
from core.security_validator import run_security_validation
from core.security import validate_environment
import json


class Command(BaseCommand):
    help = 'Validate platform security configuration'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['text', 'json'],
            default='text',
            help='Output format (default: text)'
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix issues automatically (where possible)'
        )
        parser.add_argument(
            '--strict',
            action='store_true',
            help='Use strict validation (production-level checks)'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO('🔒 Running Security Validation...'))
        
        # Run environment validation
        env_results = validate_environment()
        
        # Run comprehensive security validation
        security_results = run_security_validation()
        
        # Combine results
        combined_results = {
            'environment_validation': env_results,
            'security_validation': security_results,
            'overall_status': 'PASS' if env_results['valid'] and security_results['valid'] else 'FAIL'
        }
        
        if options['format'] == 'json':
            self.output_json(combined_results)
        else:
            self.output_text(combined_results)
        
        # Exit with appropriate code
        if not combined_results['overall_status'] == 'PASS':
            exit(1)
    
    def output_text(self, results):
        """Output results in human-readable text format"""
        env_results = results['environment_validation']
        sec_results = results['security_validation']
        
        # Environment validation results
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.HTTP_INFO('ENVIRONMENT VALIDATION'))
        self.stdout.write('='*60)
        
        if env_results['valid']:
            self.stdout.write(self.style.SUCCESS('✅ Environment configuration is valid'))
        else:
            self.stdout.write(self.style.ERROR('❌ Environment configuration has issues'))
        
        # Show errors
        if env_results['errors']:
            self.stdout.write('\n' + self.style.ERROR('ERRORS:'))
            for error in env_results['errors']:
                self.stdout.write(f'  • {error}')
        
        # Show warnings
        if env_results['warnings']:
            self.stdout.write('\n' + self.style.WARNING('WARNINGS:'))
            for warning in env_results['warnings']:
                self.stdout.write(f'  • {warning}')
        
        # Show info
        if env_results['info']:
            self.stdout.write('\n' + self.style.HTTP_INFO('INFO:'))
            for info in env_results['info']:
                self.stdout.write(f'  • {info}')
        
        # Security validation results
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.HTTP_INFO('SECURITY VALIDATION'))
        self.stdout.write('='*60)
        
        summary = sec_results['summary']
        score = sec_results.get('security_score', 0)
        grade = sec_results.get('security_grade', 'F')
        
        # Security score
        if score >= 90:
            score_style = self.style.SUCCESS
        elif score >= 70:
            score_style = self.style.WARNING
        else:
            score_style = self.style.ERROR
        
        self.stdout.write(score_style(f'Security Score: {score}/100 (Grade: {grade})'))
        self.stdout.write(f'Severity Level: {summary["severity"]}')
        self.stdout.write(f'Environment: {summary["environment"]}')
        
        # Show issues
        if sec_results['issues']:
            self.stdout.write('\n' + self.style.ERROR('CRITICAL ISSUES:'))
            for issue in sec_results['issues']:
                self.stdout.write(f'  • {issue}')
        
        # Show warnings
        if sec_results['warnings']:
            self.stdout.write('\n' + self.style.WARNING('WARNINGS:'))
            for warning in sec_results['warnings']:
                self.stdout.write(f'  • {warning}')
        
        # Show recommendations
        if sec_results['recommendations']:
            self.stdout.write('\n' + self.style.HTTP_INFO('RECOMMENDATIONS:'))
            for rec in sec_results['recommendations']:
                self.stdout.write(f'  • {rec}')
        
        # Overall status
        self.stdout.write('\n' + '='*60)
        if results['overall_status'] == 'PASS':
            self.stdout.write(self.style.SUCCESS('✅ OVERALL STATUS: SECURE'))
        else:
            self.stdout.write(self.style.ERROR('❌ OVERALL STATUS: NEEDS ATTENTION'))
        self.stdout.write('='*60)
        
        # Provide next steps
        if results['overall_status'] != 'PASS':
            self.stdout.write('\n' + self.style.HTTP_INFO('NEXT STEPS:'))
            self.stdout.write('1. Address all critical issues immediately')
            self.stdout.write('2. Review and fix warnings')  
            self.stdout.write('3. Re-run validation: python manage.py validate_security')
            self.stdout.write('4. Consider implementing recommendations')
    
    def output_json(self, results):
        """Output results in JSON format"""
        self.stdout.write(json.dumps(results, indent=2, default=str))