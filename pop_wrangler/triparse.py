from analytics.pa_parser import PaWrangler
import time
import sys

def main():
    try:
        if sys.argv[1] == 'pa_neg':
            data = PaWrangler(sys.argv[2])
            data.truss()
            data.wrangle()
            data.print_to_file()
        else:
            print("You ask too much of me!")
    except Exception as e:
        print(e)
        print("\n\nSomething has clearly gone awry.\n\nIf you believe the script is to blame, please describe your error in the issues section of this projects repository:\n\nhttps://github.com/alamancefoods/pop_wrangler/issues\n\n")

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("\n--- Finished in %s seconds ---\n" % (time.time() - start_time))

