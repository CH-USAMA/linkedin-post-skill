"""Download the open-licensed (SIL OFL) fonts used by templates.py into <skill>/assets/fonts.
Anton, Caveat, JetBrains Mono, Inter. Run once: python3 tools/fetch_fonts.py"""
import os, re, urllib.request
DEST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts")
CSS = ("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900"
       "&family=Anton&family=Caveat:wght@700&family=JetBrains+Mono:wght@700")
NAMES = {("Anton", "400"): "Anton.ttf", ("Caveat", "700"): "Caveat.ttf", ("JetBrains Mono", "700"): "JBMono.ttf",
         ("Inter", "400"): "Inter-Regular.ttf", ("Inter", "500"): "Inter-Medium.ttf", ("Inter", "600"): "Inter-SemiBold.ttf",
         ("Inter", "700"): "Inter-Bold.ttf", ("Inter", "800"): "Inter-ExtraBold.ttf", ("Inter", "900"): "Inter-Black.ttf"}
def main():
    os.makedirs(DEST, exist_ok=True)
    css = urllib.request.urlopen(urllib.request.Request(CSS, headers={"User-Agent": "Wget"})).read().decode()
    for fam, wt, url in re.findall(r"font-family: '([^']+)';.*?font-weight: (\d+);.*?url\((https://[^)]+\.ttf)\)", css, re.S):
        name = NAMES.get((fam, wt))
        if name:
            urllib.request.urlretrieve(url, os.path.join(DEST, name)); print("saved", name)
if __name__ == "__main__": main()
