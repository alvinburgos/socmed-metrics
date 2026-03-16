# Socmed Metrics

Collects metrics from Facebook in order to track follows/likes of pages of various political parties and figures, organizations, individuals, etc, and produces a dashboard that displays their historical growth. Helps track for anomalies like botting and brigading.

## Structure

The main files are:
- `extract_data.py` - Given a json file of the list of pages to track, collects follow data at the current point in time and writes them to a file. Run as frequently as needed (e.g. daily)
- `plotter.py` - displays a page that groups every entity being tracked (political party? individual? influencer? etc.) and displays their change relative to a baseline time.
- `scripts/` - The directory where various scripts used in the development of this project are stored, i.e. prototypes, parsing.
- `ansible/` - Deployment scripts for the project.
