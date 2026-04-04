# Assign codes to free text

## Data availability statement

1. Create table `postgres.daan_822.data_available_statement`, a list of all the unique statements to assign a code

2. Define the list of codes based on a [previous survey](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0194768) of PLOS ONE publications.

    - 0: statement missing
        - Any paper where the data availability statement is missing
    - 1: Not applicable
        - Should be mutually exclusive with other codes
    - 2: Not stated
        - Should be mutually exclusive with other codes
    - 3: Data used is in paper
    - 4: Data available in the Supplemental Information
    - 5: Data available in a public respository
        - Attempt to use regular expressions to extract links
    - 6: Data available upon request
    - 7: Restricted access to data
    - 8: Other
        - Any paper where a statement is present but a category 1 through 7 was not assigned

The original paper breaks out "In paper and Supplemental Information" and "combined" into diferent categories. We're going to code each paper with multiple codes, where applicable.

For llm prompt optimization, I've converted these to slugs.

3. Run a pipeline that
    - reads from `postgres.daan_822.data_available_statement`,
    - sends a prompt and the value to an LLM, then
    - writes the LLM response back to a table `postgres.daan_822.data_available_coded`


