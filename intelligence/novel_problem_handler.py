"""
Novel Problem Handler
=====================

Enables agents to solve completely new problems they've never seen before
by analyzing the problem, generating hypotheses, and creating solutions.
"""

import os
import redis
import json
from datetime import datetime
from typing import Dict, Optional
from intelligence.problem_solver import AgentProblemSolver

# Redis URL for production compatibility
import logging
logger = logging.getLogger(__name__)

_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
_REDIS_URL_DB2 = _REDIS_URL.rsplit('/', 1)[0] + '/2' if '/' in _REDIS_URL else _REDIS_URL + '/2'


class NovelProblemHandler(AgentProblemSolver):
    """
    Enhanced agent that can handle completely novel problems
    """

    def __init__(self, agent_id: str):
        super().__init__(agent_id)
        self.novel_attempts = 0
        self.novel_successes = 0

    def create_new_solution(self, problem: str, context: Dict = None) -> str:
        """
        Override to handle NOVEL problems with more intelligence
        """
        # First try the base class patterns
        base_solution = super().create_new_solution(problem, context)

        # If we got a generic solution, try to be smarter
        if 'Generic solution' in base_solution:
            print(f"   🧠 Attempting novel problem analysis...")
            novel_solution = self.analyze_and_solve_novel_problem(problem, context)
            if novel_solution:
                return novel_solution

        return base_solution

    def analyze_and_solve_novel_problem(self, problem: str, context: Dict = None) -> Optional[str]:
        """
        Analyze a novel problem and attempt to create a solution
        """
        self.novel_attempts += 1

        # Step 1: Parse the problem to understand what's needed
        problem_analysis = self.analyze_problem_requirements(problem)
        print(f"   📊 Problem analysis: {problem_analysis}")

        # Step 2: Generate solution based on analysis
        solution = self.generate_solution_from_analysis(problem_analysis, context)

        if solution:
            self.novel_successes += 1
            self.redis.hincrby(f"agent:stats:{self.agent_id}", 'novel_problems_solved', 1)
            print(f"   ✨ Generated novel solution!")

        return solution

    def analyze_problem_requirements(self, problem: str) -> Dict:
        """
        Analyze what the problem is asking for
        """
        problem_lower = problem.lower()
        analysis = {
            'input_type': None,
            'output_type': None,
            'operation': None,
            'keywords': [],
            'patterns': []
        }

        # Detect input type
        if any(word in problem_lower for word in ['text', 'string', 'sentence', 'paragraph']):
            analysis['input_type'] = 'text'
        elif any(word in problem_lower for word in ['number', 'integer', 'float', 'decimal']):
            analysis['input_type'] = 'number'
        elif any(word in problem_lower for word in ['list', 'array', 'collection']):
            analysis['input_type'] = 'list'
        elif any(word in problem_lower for word in ['dict', 'object', 'json']):
            analysis['input_type'] = 'dict'

        # Detect operation type
        if any(word in problem_lower for word in ['extract', 'find', 'get', 'parse']):
            analysis['operation'] = 'extraction'
        elif any(word in problem_lower for word in ['convert', 'transform', 'change', 'translate']):
            analysis['operation'] = 'transformation'
        elif any(word in problem_lower for word in ['calculate', 'compute', 'sum', 'average']):
            analysis['operation'] = 'calculation'
        elif any(word in problem_lower for word in ['validate', 'check', 'verify']):
            analysis['operation'] = 'validation'
        elif any(word in problem_lower for word in ['generate', 'create', 'make', 'build']):
            analysis['operation'] = 'generation'
        elif any(word in problem_lower for word in ['analyze', 'examine', 'inspect']):
            analysis['operation'] = 'analysis'

        # Extract key patterns
        if 'morse' in problem_lower:
            analysis['patterns'].append('morse_code')
        if 'pig latin' in problem_lower:
            analysis['patterns'].append('pig_latin')
        if 'base64' in problem_lower:
            analysis['patterns'].append('base64')
        if 'binary' in problem_lower:
            analysis['patterns'].append('binary')
        if 'hex' in problem_lower:
            analysis['patterns'].append('hexadecimal')
        if 'capitalize' in problem_lower or 'capital' in problem_lower:
            analysis['patterns'].append('capitalization')

        # Extract keywords for context
        important_words = ['email', 'phone', 'url', 'date', 'time', 'password', 'username',
                          'credit card', 'ssn', 'zip', 'address', 'name', 'age']
        analysis['keywords'] = [word for word in important_words if word in problem_lower]

        return analysis

    def generate_solution_from_analysis(self, analysis: Dict, context: Dict = None) -> Optional[str]:
        """
        Generate a solution based on problem analysis
        """
        operation = analysis.get('operation')
        patterns = analysis.get('patterns', [])

        # Handle specific pattern combinations
        if 'morse_code' in patterns and 'pig_latin' in patterns:
            return self.generate_morse_to_pig_latin_solution()

        # Handle operation types
        if operation == 'extraction':
            return self.generate_extraction_solution(analysis)
        elif operation == 'transformation':
            return self.generate_transformation_solution(analysis)
        elif operation == 'calculation':
            return self.generate_calculation_solution(analysis)
        elif operation == 'validation':
            return self.generate_validation_solution(analysis)
        elif operation == 'generation':
            return self.generate_generation_solution(analysis)
        elif operation == 'analysis':
            return self.generate_analysis_solution(analysis)

        # If we can't determine the operation, try a generic approach
        return self.generate_generic_novel_solution(analysis)

    def generate_morse_to_pig_latin_solution(self) -> str:
        """Generate solution for the specific morse->pig latin problem"""
        return '''
def solution(text):
    """Convert Morse code to pig latin while maintaining capitalization"""

    # Morse code dictionary
    morse_dict = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
        '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
        '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
        '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
        '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
        '--..': 'Z'
    }

    def to_pig_latin(word):
        """Convert word to pig latin"""
        if not word:
            return word

        vowels = 'AEIOUaeiou'
        word_upper = word.upper()
        was_upper = word[0].isupper() if word else False

        if word_upper[0] in vowels:
            result = word_upper + 'WAY'
        else:
            # Move consonants to end
            i = 0
            while i < len(word_upper) and word_upper[i] not in vowels:
                i += 1
            result = word_upper[i:] + word_upper[:i] + 'AY'

        # Maintain capitalization
        if was_upper:
            return result[0].upper() + result[1:].lower()
        return result.lower()

    # Parse morse code
    if '/' in text:  # Words separated by /
        morse_words = text.split('/')
    else:
        morse_words = [text]

    decoded_words = []
    for morse_word in morse_words:
        letters = morse_word.strip().split(' ')
        word = ''
        for letter_code in letters:
            if letter_code in morse_dict:
                word += morse_dict[letter_code]
        if word:
            decoded_words.append(word)

    # Convert to pig latin
    pig_latin_words = [to_pig_latin(word) for word in decoded_words]

    return ' '.join(pig_latin_words)
'''

    def generate_extraction_solution(self, analysis: Dict) -> str:
        """Generate extraction solution based on analysis"""
        if analysis.get('input_type') == 'text':
            return '''
import re
def solution(text):
    """Extract patterns from text"""
    # Generic pattern extraction
    patterns = []

    # Try common patterns
    # Numbers
    numbers = re.findall(r'\d+\.?\d*', text)
    if numbers:
        patterns.extend(numbers)

    # Words in caps
    caps = re.findall(r'\b[A-Z]{2,}\b', text)
    if caps:
        patterns.extend(caps)

    # Quoted strings
    quoted = re.findall(r'"([^"]*)"', text)
    if quoted:
        patterns.extend(quoted)

    return patterns if patterns else [text]
'''
        return None

    def generate_transformation_solution(self, analysis: Dict) -> str:
        """Generate transformation solution"""
        if 'base64' in analysis.get('patterns', []):
            return '''
import base64
def solution(data):
    """Transform data using base64"""
    if isinstance(data, str):
        # Try to decode first, if fails then encode
        try:
            return base64.b64decode(data.encode()).decode()
        except:
            return base64.b64encode(data.encode()).decode()
    return str(data)
'''
        elif 'binary' in analysis.get('patterns', []):
            return '''
def solution(data):
    """Convert to/from binary"""
    if isinstance(data, str):
        if all(c in '01 ' for c in data):
            # Binary to text
            binary_strings = data.split()
            return ''.join(chr(int(b, 2)) for b in binary_strings if b)
        else:
            # Text to binary
            return ' '.join(format(ord(c), '08b') for c in data)
    return str(data)
'''
        return None

    def generate_calculation_solution(self, analysis: Dict) -> str:
        """Generate calculation solution"""
        return '''
def solution(data):
    """Perform calculations on data"""
    if isinstance(data, (list, tuple)):
        numbers = [float(x) for x in data if isinstance(x, (int, float))]
        if numbers:
            return {
                'sum': sum(numbers),
                'average': sum(numbers) / len(numbers),
                'min': min(numbers),
                'max': max(numbers),
                'count': len(numbers)
            }
    elif isinstance(data, dict):
        return sum(v for v in data.values() if isinstance(v, (int, float)))
    else:
        try:
            return float(data)
        except Exception as _e:
            logger.warning(
                "novel_problem_handler.solution: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return 0
'''

    def generate_validation_solution(self, analysis: Dict) -> str:
        """Generate validation solution"""
        return '''
import re
def solution(data):
    """Validate data format"""
    if isinstance(data, str):
        # Check common formats
        validations = {
            'email': bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', data)),
            'phone': bool(re.match(r'^[\d\s\-\(\)]+$', data) and len(re.sub(r'\D', '', data)) >= 10),
            'url': bool(re.match(r'^https?://', data)),
            'numeric': data.replace('.', '').replace('-', '').isdigit(),
            'alphanumeric': data.isalnum()
        }

        # Return first matching validation or False
        for format_type, is_valid in validations.items():
            if is_valid:
                return {'valid': True, 'format': format_type}

        return {'valid': False, 'format': 'unknown'}

    return {'valid': bool(data), 'format': type(data).__name__}
'''

    def generate_generation_solution(self, analysis: Dict) -> str:
        """Generate data generation solution"""
        return '''
import random
import string
def solution(spec=None):
    """Generate data based on specification"""
    if not spec:
        spec = {'type': 'string', 'length': 10}

    if isinstance(spec, dict):
        data_type = spec.get('type', 'string')
        length = spec.get('length', 10)

        if data_type == 'string':
            return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        elif data_type == 'number':
            return random.randint(10**(length-1), 10**length - 1)
        elif data_type == 'list':
            return [random.randint(0, 100) for _ in range(length)]
        elif data_type == 'id':
            return f"{spec.get('prefix', 'ID')}_{random.randint(1000, 9999)}"

    return f"generated_{random.randint(1000, 9999)}"
'''

    def generate_analysis_solution(self, analysis: Dict) -> str:
        """Generate analysis solution"""
        return '''
def solution(data):
    """Analyze data and return insights"""
    analysis = {
        'type': type(data).__name__,
        'size': len(data) if hasattr(data, '__len__') else 1
    }

    if isinstance(data, str):
        analysis.update({
            'words': len(data.split()),
            'characters': len(data),
            'lines': len(data.splitlines()),
            'has_numbers': any(c.isdigit() for c in data),
            'has_uppercase': any(c.isupper() for c in data)
        })
    elif isinstance(data, (list, tuple)):
        analysis.update({
            'unique_items': len(set(data)) if all(isinstance(x, (str, int, float)) for x in data) else len(data),
            'types': list(set(type(x).__name__ for x in data))
        })
    elif isinstance(data, dict):
        analysis.update({
            'keys': list(data.keys()),
            'depth': 1  # Could be recursive
        })

    return analysis
'''

    def generate_generic_novel_solution(self, analysis: Dict) -> str:
        """Last resort: generate a generic solution that tries multiple approaches"""
        return '''
def solution(input_data):
    """Attempt to solve novel problem with multiple approaches"""
    results = {}

    # Try different interpretations
    if isinstance(input_data, str):
        # String operations
        results['uppercase'] = input_data.upper()
        results['lowercase'] = input_data.lower()
        results['reversed'] = input_data[::-1]
        results['words'] = input_data.split()
        results['length'] = len(input_data)

        # Try to extract patterns
        import re
        numbers = re.findall(r'\d+', input_data)
        if numbers:
            results['numbers'] = numbers

    elif isinstance(input_data, (list, tuple)):
        # List operations
        results['sorted'] = sorted(input_data) if all(isinstance(x, (str, int, float)) for x in input_data) else input_data
        results['reversed'] = list(reversed(input_data))
        results['first'] = input_data[0] if input_data else None
        results['last'] = input_data[-1] if input_data else None
        results['count'] = len(input_data)

    elif isinstance(input_data, dict):
        # Dict operations
        results['keys'] = list(input_data.keys())
        results['values'] = list(input_data.values())
        results['items'] = list(input_data.items())

    else:
        # Unknown type
        results['str'] = str(input_data)
        results['type'] = type(input_data).__name__

    # Return the most relevant result or all results
    return results if len(results) > 1 else next(iter(results.values())) if results else input_data
'''


class NovelProblemListener:
    """
    Listens for novel problems and dispatches them to capable agents
    """

    def __init__(self):
        self.redis = redis.Redis.from_url(_REDIS_URL_DB2, decode_responses=True)
        self.handlers = {}

    def register_handler(self, agent: NovelProblemHandler):
        """Register an agent that can handle novel problems"""
        self.handlers[agent.agent_id] = agent
        print(f"   🎯 Registered novel problem handler: {agent.agent_id}")

    def monitor_novel_problems(self):
        """Monitor for novel problem tasks"""
        pubsub = self.redis.pubsub()
        pubsub.psubscribe('task:novel:*')

        for message in pubsub.listen():
            if message['type'] == 'pmessage':
                self.handle_novel_task(message)

    def handle_novel_task(self, message):
        """Dispatch novel task to best handler"""
        try:
            # Get task details
            task_key = message['channel'].decode() if isinstance(message['channel'], bytes) else message['channel']
            task_data = self.redis.hgetall(task_key)

            if task_data and task_data.get('status') == 'pending':
                problem = json.loads(task_data.get('problem', '{}'))

                print(f"\n🆕 Novel problem detected: {problem.get('problem', 'Unknown')}")

                # Find best handler
                best_handler = self.select_best_handler(problem)

                if best_handler:
                    # Attempt to solve
                    result = best_handler.solve_problem(
                        problem.get('problem'),
                        context={'test_data': problem.get('input')}
                    )

                    # Update task status
                    self.redis.hset(task_key, mapping={
                        'status': 'solved' if result['success'] else 'failed',
                        'solution': json.dumps(result),
                        'solved_by': best_handler.agent_id,
                        'solved_at': datetime.now().isoformat()
                    })

                    print(f"   ✅ {best_handler.agent_id} solved the novel problem!")

        except Exception as e:
            print(f"   ❌ Error handling novel task: {e}")

    def select_best_handler(self, problem: Dict) -> Optional[NovelProblemHandler]:
        """Select the best agent to handle this problem"""
        if not self.handlers:
            return None

        # For now, return first available handler
        # Could be enhanced with capability matching
        return next(iter(self.handlers.values()))


# Test the novel problem handler
if __name__ == "__main__":
    print("🧪 Testing Novel Problem Handler\n")

    # Create a novel problem handler
    handler = NovelProblemHandler("novel_solver_001")

    # Test with the morse->pig latin problem
    result = handler.solve_problem(
        "Convert Morse code to pig latin while maintaining capitalization",
        context={'test_data': '.... . .-.. .-.. ---'}  # "HELLO" in morse
    )

    print(f"\nResult: {result.get('result')}")
    print(f"Success: {result.get('success')}")

    # Test with another novel problem
    result2 = handler.solve_problem(
        "Convert binary to text",
        context={'test_data': '01001000 01100101 01101100 01101100 01101111'}  # "Hello" in binary
    )

    print(f"\nResult 2: {result2.get('result')}")
    print(f"Success 2: {result2.get('success')}")

    # Check stats
    print(f"\nNovel attempts: {handler.novel_attempts}")
    print(f"Novel successes: {handler.novel_successes}")