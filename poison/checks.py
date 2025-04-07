import importlib.util

REQUIRED_MODULES = [
    "os",
    "asyncio",
    "aiogram",
    "dotenv",
    "aiogram.enums",
    "aiogram.client.default",
    "aiogram.types",
    "aiogram.filters",
    "storage.database",
    "poison.gemini",
    "poison.checks"
]

def check_dependencies():
    print("🔍 Checking dependencies...\n")
    for module in REQUIRED_MODULES:
        spec = importlib.util.find_spec(module)
        if spec is not None:
            print(f"✅ {module}")
        else:
            print(f"❌ {module}")
    print("\nDependency check complete.\n")
