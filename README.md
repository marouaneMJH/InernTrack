# Internship Sync

A Python application that automatically scrapes internship opportunities using JobSpy and synchronizes them with Notion databases.

## Features

- **Multi-site scraping**: Fetches internship data from Indeed, LinkedIn, and Stack Overflow
- **Notion integration**: Automatically creates companies and job offers in your Notion workspace
- **Intelligent filtering**: Identifies internship-specific positions using keyword detection
- **Deduplication**: Removes duplicate offers based on URLs
- **Dry run mode**: Test the pipeline without making changes to Notion
- **GitHub Actions support**: Schedule automatic runs

## Setup

### 1. Create Notion Integration

1. Go to [Notion Developers](https://developers.notion.com/)
2. Create a new integration and get your `NOTION_TOKEN`
3. Share your databases with the integration

### 2. Get Database IDs

1. Open each database in Notion
2. Copy the database ID from the URL (32-character string)
3. Or use the Notion API to list databases

### 3. Configure Environment

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in your actual values:
   ```env
   NOTION_TOKEN=secret_your_actual_token
   DB_COMPANIES_ID=your_companies_database_id
   DB_OFFERS_ID=your_offers_database_id
   # ... other database IDs
   ```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Local Execution

Run the scraper locally:

```bash
bash scripts/run.sh
```

### Dry Run Mode

Test without making changes to Notion:

```bash
# Set DRY_RUN=true in .env
python src/main.py
```

### GitHub Actions Deployment

1. Add the following secrets to your GitHub repository:
   - `NOTION_TOKEN`
   - `DB_COMPANIES_ID`
   - `DB_OFFERS_ID`
   - `DB_APPLICATIONS_ID`
   - `DB_CONTACTS_ID`
   - `DB_DOCUMENTS_ID`
   - `DB_OFFERS_RECEIVED_ID`

2. The workflow will run daily at 09:00 UTC or can be triggered manually

## Configuration

### Search Parameters

- `SEARCH_TERMS`: Comma-separated keywords (e.g., "internship,stage,intern")
- `LOCATIONS`: Comma-separated locations (e.g., "morocco,Remote")
- `RESULTS_WANTED`: Maximum number of results per search

### Supported Countries

When configuring `LOCATIONS`, use these supported country names (case-insensitive):

`argentina`, `australia`, `austria`, `bahrain`, `bangladesh`, `belgium`, `bulgaria`, `brazil`, `canada`, `chile`, `china`, `colombia`, `costa rica`, `croatia`, `cyprus`, `czech republic`, `czechia`, `denmark`, `ecuador`, `egypt`, `estonia`, `finland`, `france`, `germany`, `greece`, `hong kong`, `hungary`, `india`, `indonesia`, `ireland`, `israel`, `italy`, `japan`, `kuwait`, `latvia`, `lithuania`, `luxembourg`, `malaysia`, `malta`, `mexico`, `morocco`, `netherlands`, `new zealand`, `nigeria`, `norway`, `oman`, `pakistan`, `panama`, `peru`, `philippines`, `poland`, `portugal`, `qatar`, `romania`, `saudi arabia`, `singapore`, `slovakia`, `slovenia`, `south africa`, `south korea`, `spain`, `sweden`, `switzerland`, `taiwan`, `thailand`, `turkey`, `ukraine`, `united arab emirates`, `united kingdom`, `united states`, `uruguay`, `venezuela`, `vietnam`, `worldwide`, `remote`

### Notion Database Properties

Make sure your Notion databases have the following properties:

#### Companies Database
- `Name` (Title)
- `Website` (URL)
- `Industry` (Select)
- `Country` (Rich Text)
- `Description` (Rich Text)

#### Offers Database
- `Offer Title` (Title)
- `Offer Link` (URL)
- `Description` (Rich Text)
- `Status` (Select)
- `Created On` (Date)
- `Location` (Rich Text)

## Project Structure

```
internship-sync/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── main.py              # Main pipeline
│   ├── config.py            # Configuration management
│   ├── jobspy_client.py     # Job scraping logic
│   ├── notion_client.py     # Notion API integration
│   ├── normalizer.py        # Data transformation
│   ├── dedupe.py           # Duplicate removal
│   └── logger_setup.py     # Logging configuration
├── scripts/
│   └── run.sh              # Execution script
└── .github/
    └── workflows/
        └── schedule.yml    # GitHub Actions workflow
```

## Improvements & Extensions

1. **Property Mapping**: Customize `notion_client.py` to match your exact Notion property names
2. **Relations**: Add logic to create relationships between companies and offers
3. **Rate Limiting**: Implement backoff strategies for API calls
4. **Document Management**: Add support for uploading resumes and cover letters
5. **Web Dashboard**: Create a React frontend for offer approval workflows

## Troubleshooting

### Common Issues

1. **Property names don't match**: Update property names in `notion_client.py` to match your Notion schema
2. **Rate limiting**: Add delays between API calls if you hit Notion rate limits
3. **JobSpy installation**: If the pip package isn't available, clone from GitHub and adapt imports

### Logging

Set `LOG_LEVEL=DEBUG` in your `.env` file for detailed execution logs.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request