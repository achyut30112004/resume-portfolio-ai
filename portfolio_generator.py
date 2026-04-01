from jinja2 import Environment, FileSystemLoader

def generate_portfolio(data, output_file="portfolio.html"):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("portfolio.html")

    html_content = template.render(
        name=data.get("name", "Unknown"),
        email=data.get("email", "N/A"),
        phone=data.get("phone", "N/A"),
        skills=data.get("skills", []),
        experience=data.get("experience", []),
        education=data.get("education", [])
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return output_file