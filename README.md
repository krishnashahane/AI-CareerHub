# CareerHub — India Job Market Visualizer

An interactive treemap visualization of **100 occupations** across the Indian economy, covering **530M+ jobs**. Built by **Krishna Shahane**.

## Features

- **Interactive Treemap**: Each rectangle's area is proportional to total employment in that occupation
- **Multiple Data Layers**: Toggle between four color-coded views:
  - **Growth Outlook** — Projected employment growth rate
  - **Median Pay** — Annual salary in INR (₹)
  - **Education** — Minimum education requirement
  - **Digital AI Exposure** — LLM-estimated AI disruption score (0–10)
- **Search**: Filter and highlight occupations by name or category
- **Rich Tooltips**: Hover over any tile to see detailed stats
- **Dashboard Stats**: Weighted averages, histograms, tier breakdowns, and cross-tabulations

## Data Coverage

Occupations span 15 sectors of the Indian economy:

| Sector | Example Occupations |
|--------|-------------------|
| Agriculture & Allied | Farmers, Dairy Workers, Fishery Workers |
| Information Technology | Software Developers, AI/ML Engineers, Cybersecurity |
| Healthcare | Doctors, Nurses, AYUSH Practitioners |
| Construction & Infrastructure | Construction Laborers, Civil Engineers, Electricians |
| Manufacturing | Textile Workers, Automobile Assembly, Pharma |
| Banking & Finance | Bank Clerks, CAs, Financial Analysts |
| Education & Training | School Teachers, Professors, Coaching Teachers |
| Retail & Commerce | Retail Salespersons, E-Commerce, Delivery Riders |
| Transport & Logistics | Truck Drivers, Auto-Rickshaw Drivers, Railway Workers |
| Legal & Government | Lawyers, Government Clerks, Police Officers |
| Hospitality & Tourism | Hotel Staff, Chefs, Tour Guides |
| Media & Entertainment | Content Writers, Graphic Designers, Film Production |
| Services & Maintenance | Domestic Helpers, Security Guards, Beauticians |
| Business Services | BPO Agents, HR Managers, Data Entry Operators |
| Telecom & Energy | Telecom Engineers, Solar Technicians, Mining Workers |

## Data Sources

- [National Career Service (NCS)](https://www.ncs.gov.in/) — Ministry of Labour & Employment
- [MOSPI](https://www.mospi.gov.in/) — Ministry of Statistics and Programme Implementation
- Industry reports and NASSCOM data for IT sector estimates
- AI Exposure scores generated via LLM analysis

## Quick Start

```bash
cd jobs/site
python3 -m http.server 8000
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

## Tech Stack

- **Frontend**: Vanilla HTML/CSS/JavaScript (single-file, no dependencies)
- **Visualization**: Canvas-based squarified treemap
- **Data**: Static JSON (100 occupations with employment, pay, outlook, education, and AI exposure data)

## Currency & Units

- All salaries are in **Indian Rupees (INR/₹)** per annum
- Employment numbers reflect estimated Indian workforce figures
- Pay displayed in Lakhs (L) format: ₹1L = ₹1,00,000

## License

MIT

---

*Built by Krishna Shahane*
