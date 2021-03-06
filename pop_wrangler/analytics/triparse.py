from excelerator.pc_parser import PaWrangler as paW
from excelerator.pa_scraper import PaScraper as paS
from excelerator.file_cleaner import FileCleaner as fC
import time
import sys, traceback

def main():
    try:
        if sys.argv[1] == 'wrangle':
            data = paW(sys.argv[2], day_count = sys.argv[3])
            data.truss()
            data.wrangle()
            data.print_to_file()
        elif sys.argv[1] == 'scrape':
            master = paS(sys.argv[2])
            master.write_to_excel()
        elif sys.argv[1] == 'clean':
            dataframe = fC(sys.argv[2])
            dataframe.clean()
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

