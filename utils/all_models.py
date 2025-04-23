import os

def get_all_models():
    """
    Returns a list of all files in the models/ directory.
    """
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(repo_root, 'models')
    if not os.path.exists(models_dir):
        return []
    return [f for f in os.listdir(models_dir) if os.path.isfile(os.path.join(models_dir, f))]

if __name__ == "__main__":
    # Example usage
    model_files = get_all_models()
    for model_file in model_files:
        print(model_file)