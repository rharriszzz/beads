"""Historical R161 check after detector freeze; never an inference input."""
from pathlib import Path
from photo2.r323 import evaluate

def main():
    evaluate.OUT=Path(__file__).parent/'results'
    evaluate.main()
if __name__=='__main__':main()
