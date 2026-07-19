
import sys
sys.path.insert(0, 'src')

output = []
output.append("Testing imports...")

try:
    from healing_agent.app import create_app
    output.append("OK create_app imported successfully")
except Exception as e:
    output.append(f"FAILED to import create_app: {type(e)} {str(e)}")
    import traceback
    output.append(traceback.format_exc())

try:
    from healing_agent.modules.sandbox_verification.adapter import SandboxTestRunnerAdapter
    output.append("OK SandboxTestRunnerAdapter imported successfully")
except Exception as e:
    output.append(f"FAILED to import SandboxTestRunnerAdapter: {type(e)} {str(e)}")
    import traceback
    output.append(traceback.format_exc())

try:
    from healing_agent.modules.contracts import OrchestrationModules
    output.append("OK OrchestrationModules imported successfully")
except Exception as e:
    output.append(f"FAILED to import OrchestrationModules: {type(e)} {str(e)}")
    import traceback
    output.append(traceback.format_exc())

with open('test_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print('\n'.join(output))
