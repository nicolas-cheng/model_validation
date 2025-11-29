import sys
from pathlib import Path

# Add the project root to sys.path to ensure imports work correctly
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from source.ochestration_agent import main

if __name__ == "__main__":
    main()
