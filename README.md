
## Module Breakdown:
* Pandas (munger)
* XlsxWriter (excel whisperer)

### Code Practices:
Going forward, effort should be made to separate excel polish from pandas polish. Currently, I have a single class that handles the whole shebang. Soon, I would like to have some genaralized classes for each, I'm just not there yet.

#### PaWrangler Class:
##### Initialization:
``` python
PaWrangler(self, file)
```
Accepts excel file and initializes PaWrangler object.

##### Methods:
``` python
PaWrangler.truss()
```
Processes excel file into pandas dataframe.

``` python
PaWrangler.wrangle()
```
Iterates through dataframes, munging data according to specifications.

``` python
PaWrangler.print_to_file()
```
Prints formatted data to a timestamped excel file. 
