from analytics.pa_parser import PaWrangler as paW
from analytics.pc_parser import PaWrangler as pcW
import time
import sys, traceback

def main():
    try:
        if sys.argv[1] == 'pa_neg':
            data = paW(sys.argv[2])
            data.truss()
            data.wrangle()
            data.print_to_file()
        elif sys.argv[1] == 'pc_neg':
            data = pcW(sys.argv[2])
            data.truss()
            data.wrangle()
            data.print_to_file()
        elif sys.argv[1] == 'dry_run':
            data = paW(sys.argv[2])
            data.truss()
            data.wrangle()
        else:
            print("You ask too much of me!")
    except Exception as e:
        print(e)
        print(sys.exc_info()[0])
        traceback.print_exc(file=sys.stdout)
        print("\n\nSomething has clearly gone awry.\n\nIf you believe the script is to blame, please describe your error in the issues section of this projects repository:\n\nhttps://github.com/alamancefoods/pop_wrangler/issues\n\n")

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("\n--- Finished in %s seconds ---\n" % (time.time() - start_time))

