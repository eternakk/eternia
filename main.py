from eterna_interface import EternaInterface
from navigator import eterna_cli

def main():
    eterna = EternaInterface()
    print("\n🚀 Initializing Eterna...\n")



    eterna_cli(eterna)

if __name__ == "__main__":
    main()
