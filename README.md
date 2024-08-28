# rightmove-property-scraper

This repository contains a Scrapy-based project designed to scrape property listing data from the Rightmove website. The project is divided into four main subtasks, each implemented as a separate Scrapy spider within different modules. The project uses the Poetry environment for dependency management.

## Project Structure

```
.
├── .gitignore
├── poetry.lock
├── pyproject.toml
├── rm_scraper
│   ├── spiders
│   │   └── rm_spider.py
├── rightmove_scraper
│   ├── spiders
│   │   └── rightmove_spider.py
└── rmpipeline
    ├── rmpipeline
    │   ├── pipelines.py
    │   ├── settings.py
    │   ├── config.yml
    │   ├── spiders
    │   │   ├── rmpipeline1_spider.py
    │   │   ├── rmpipeline2_spider.py
    │   │   └── rmpipeline3_spider.py
    ├── rmpipeline_NG118BL_2024-06-10.json
    ├── rmpipeline_NG118BL_2024-06-13.json
├── upload_outputs.py
```

## Setting Up the Environment

### Prerequisites
- Ensure you have [Poetry](https://python-poetry.org/docs/#installation) installed on your machine.
- Python 3.8 or later.

### Steps to Set Up
1. Clone the repository:
   ```bash
   git clone https://github.com/org-datafella/df-web-whisperer.git
   cd df-web-whisperer
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

## Subtask 1: Extract Listing Names

### Description
The objective of this subtask is to extract listing names from the Rightmove website and save them in a CSV file.

### Files
- `rightmove_scraper/spiders/rightmove_spider.py`: The spider that successfully crawls all pages and stores scraped data in `listings.csv`.
- `rm_scraper/spiders/rm_spider.py`: The initial attempt which only scraped the first page of results, resulting in `listings1.csv`.



### Steps to Execute
1. Navigate to the `rightmove_scraper` directory:
   ```bash
   cd rightmove_scraper
   ```
2. Run the spider:
   ```bash
   scrapy crawl rightmove_spider -o listings.csv
   ```

To test the initial attempt(This only scrape the data from first page):
1. Navigate to the `rm_scraper` directory:
   ```bash
   cd rm_scraper
   ```
2. Run the spider:
   ```bash
   scrapy crawl rm_spider -o listings1.csv
   ```

## Subtasks 2, 3, 4: Robust Web Scraping Pipeline

### Description
These subtasks involve creating a robust web scraping pipeline to extract high, medium, and low-priority data from the Rightmove website.

### Files
- `rmpipeline/rmpipeline/spiders/rmpipeline1_spider.py`: Spider for high-priority data extraction.
- `rmpipeline/rmpipeline/spiders/rmpipeline2_spider.py`: Spider for medium-priority data extraction.
- `rmpipeline/rmpipeline/spiders/rmpipeline3_spider.py`: Spider for low-priority data extraction.
- `rmpipeline/rmpipeline/pipelines.py`: Defines the pipeline for saving scraped data to JSON files.
- `rmpipeline/rmpipeline/settings.py`: Contains Scrapy settings, including reading configurations from `config.yml`.
- `rmpipeline/rmpipeline/config.yml`: Configuration file to specify postcodes and other parameters.

### Steps to Execute
1. Navigate to the `rmpipeline` directory:
   ```bash
   cd rmpipeline/rmpipeline
   ```
2. Ensure the `config.yml` file is correctly configured with the target postcodes and radius:
   ```yaml
   postcodes:
     - NG118BL
   radius: 3.0
   ```
3. Run the appropriate spider for the required data extraction:
   - For high-priority data:
     ```bash
     scrapy crawl rmpipeline1_spider
     ```
     - Output file: `rmpipeline_NG118BL_2024-06-10.json`
   - For medium-priority data:
     ```bash
     scrapy crawl rmpipeline2_spider
     ```
     - Output file: `rmpipeline_NG118BL_2024-06-13.json`
   - For low-priority data:
     ```bash
     scrapy crawl rmpipeline3_spider
     ```

Each spider will generate a JSON file named using the convention `rmpipeline_<POSTCODE>_<EXTRACTED_DATE>.json`.

## Subtask 5 - Uploading Output Files to S3

### Description
The script `upload_outputs.py` is used to upload the output files to an S3 bucket.

### Steps to Execute
1. Navigate to the main directory:
   ```bash
   cd /path/to/main/directory
   ```
2. Run the upload script:
   ```bash
   python upload_outputs.py
   ```

## Issues and Solutions

### Issue 1: Initial Spider Only Scraped First Page
- **Description:** The initial spider in `rm_scraper` only scraped the first page of listings.
- **Solution:** Developed a new spider in `rightmove_scraper` that handles pagination and scrapes all pages.

### Issue 2: Configuration Management
- **Description:** Managing configurations such as postcodes and radius dynamically.
- **Solution:** Used a `config.yml` file to fetch target postcodes and other parameters, making the pipeline flexible and configurable.

### Issue 3: Data Pipeline
- **Description:** Ensuring data is saved in the correct format and structure.
- **Solution:** Implemented a custom pipeline in `pipelines.py` to write data to JSON files with the required naming convention.
 
### Issue 4: Handling Dynamic Content
- **Description:** Currently facing issues with getting data, resulting in null values. This is due to the dynamic parts on the website that Scrapy cannot handle effectively.
- **Solution:** Investigating solutions such as using Selenium for dynamic content scraping or implementing more robust error handling mechanisms within the spiders.


## Dependencies

The project uses Poetry for dependency management. Ensure you have Poetry installed, then install the dependencies by running:
```bash
poetry install
```

## Conclusion

This documentation provides a comprehensive guide to understand and execute the tasks within this repository. By following the provided steps, users can replicate the web scraping tasks and generate the required output files.

For any further questions or issues, please refer to the code comments and configurations within the repository.