"""Command line entry point: `serp-feature-ownership YOU.csv [COMPETITOR.csv ...]`."""
from pathlib import Path

import click

from . import __version__, core
from .benchmark import STATS
from .report import Report, write_excel


@click.command()
@click.argument("your_csv", type=click.Path(exists=True))
@click.argument("competitor_csv", nargs=-1, type=click.Path(exists=True))
@click.option("--top", default=10, show_default=True,
              help="You must rank at or above this position for a feature to count as winnable.")
@click.option("-o", "--output", default="serp_features", show_default=True,
              help="Report name; writes <name>.html and <name>.xlsx")
@click.version_option(__version__)
def main(your_csv, competitor_csv, top, output):
    """Show who owns the SERP features on your keywords. YOUR_CSV first, then 0-5 COMPETITOR_CSV exports.

    Built by Meer Hamza - linkedin.com/in/meerhamza-seo
    """
    if len(competitor_csv) > 5:
        raise click.BadParameter("use up to 5 competitor files")
    pairs, sites, n_kw = core.analyze(your_csv, competitor_csv, top)
    land = core.landscape(pairs, n_kw)
    own = core.ownership(pairs, sites)
    counts = pairs["status"].value_counts()

    report = Report(title="SERP feature ownership", subtitle=f"{sites[0]} vs {', '.join(sites[1:]) or 'no competitors'}",
                    tool="serp-feature-ownership")
    report.add_cards([
        ("Keywords", n_kw),
        ("Keyword + feature pairs", len(pairs)),
        ("You own (defend)", int(counts.get("defend", 0)), "good"),
        ("Competitor owns, you rank top " + str(top) + " (steal)", int(counts.get("steal", 0)), "bad"),
        ("Nobody tracked owns it (open)", int(counts.get("open", 0)), "warn"),
    ])
    report.add_benchmark(STATS[0], how_used="Your share of keywords showing each feature is set next to the 2024 "
                         "presence rate, and the build actions for videos, images, carousels and related searches "
                         "come from these insights.")
    report.add_benchmark(STATS[1], how_used="AI Overviews and zero-click results take real space on page one, so "
                         "AI Overview rows get the stat's advice: natural language answers and FAQ structured data.")
    report.add_table("Feature landscape", land, sheet="Landscape",
                     note="How often each feature appears on your keywords and what to build to win it.")
    report.add_table("Who owns what", own, sheet="Ownership", note="Keywords on which each site holds the feature.")
    for status, note in [
        ("steal", f"A competitor holds the feature and you already rank top {top}. Highest volume first."),
        ("open", f"The feature shows, no tracked site holds it, and you rank top {top}."),
        ("defend", "You hold the feature. Keep these pages fresh."),
    ]:
        report.add_table(f"{status.title()}", pairs[pairs["status"] == status].drop(columns="status"),
                         note=note, sheet=status.title())
    report.add_table("All keyword + feature pairs", pairs, sheet="All pairs",
                     note=f"'out of reach' = you rank below {top} or not at all: win the ranking first.")

    html_path = report.save_html(Path(output).with_suffix(".html"))
    xlsx_path = write_excel(report.sheets, Path(output).with_suffix(".xlsx"))
    click.secho(f"Report: {html_path}\nData:   {xlsx_path}", fg="green", bold=True)
    click.echo(land[["feature", "keywords", "you_own", "steal", "open"]].to_string(index=False))


if __name__ == "__main__":
    main()
