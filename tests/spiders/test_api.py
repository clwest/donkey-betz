# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""Test the learning details API directly"""
import redis
import json

def get_learning_details():
    try:
        r = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)

        # Get recent solutions
        solution_keys = r.keys('solution:*')[:10]
        solutions = []

        for key in solution_keys:
            try:
                solution_data = r.hgetall(key)
                if solution_data:
                    solutions.append({
                        'problem': solution_data.get('problem', 'Unknown'),
                        'code': solution_data.get('solution_code', ''),
                        'agent': solution_data.get('discovered_by', 'Unknown'),
                        'execution_time': float(solution_data.get('execution_time', 0))
                    })
            except:
                pass

        return {
            'solutions': solutions,
            'total': len(olutions)
        }
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    result = get_learning_details()
    print(json.dumps(result, indent=2))