#!/usr/bin/env python3
"""
Demonstration script that contacts the OpenAI API to analyze sentiment.

This demo generates articles about AMD, Nvidia, and Broadcom, then sends them
to the OpenAI API for sentiment analysis using the VUTS workflow.
"""

import json
import datetime
from pathlib import Path
import sys
import os

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm.sentiment_analyzer import (
    load_prompt_template,
    format_prompt,
    parse_llm_response,
    call_openai_api,
    save_llm_score
)
from market.data_fetcher import format_market_context


def create_demo_articles(base_dir: Path):
    """Create demonstration articles for AMD, Nvidia, and Broadcom."""
    print("=" * 70)
    print("CREATING DEMO ARTICLES")
    print("=" * 70)
    
    articles = []
    
    # AMD Articles (4 articles)
    amd_articles = [
        {
            "source": "demo_openai_api",
            "topic": "AMD",
            "title": "AMD Unveils Next-Gen EPYC Processors, Targets Data Center Growth",
            "url": "https://example.com/amd1",
            "published_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "content": """
Advanced Micro Devices Inc. announced its latest generation of EPYC server processors today, 
featuring enhanced performance and power efficiency for data center applications. The new chips, 
built on an advanced 3nm process, deliver up to 50% better performance per watt compared to 
previous generations.

AMD's data center segment has been a major growth driver, with market share gains against Intel 
continuing through 2024. The company reported that EPYC processors now power over 30% of cloud 
computing infrastructure globally, up from 25% a year ago.

"These processors represent a significant leap forward in data center computing," said AMD CEO 
Lisa Su. "Our customers are demanding more computational power with better energy efficiency, 
and these chips deliver on both fronts."

Analysts at Goldman Sachs raised their price target following the announcement, citing AMD's 
strong position in the rapidly growing AI and cloud computing markets. The company's stock 
rose 4.2% in morning trading.
""".strip(),
            "author": "Tech News Staff",
            "sentiment_context": "product_announcement"
        },
        {
            "source": "demo_openai_api",
            "topic": "AMD",
            "title": "AMD Beats Q4 Earnings Expectations on Strong Data Center Demand",
            "url": "https://example.com/amd2",
            "published_at": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=2)).isoformat(),
            "content": """
AMD reported fourth-quarter earnings that exceeded Wall Street expectations, driven by robust 
demand for its data center and AI chips. Revenue came in at $6.8 billion, up 18% year-over-year 
and above consensus estimates of $6.5 billion.

Earnings per share of $0.92 beat the expected $0.85, marking the company's fifth consecutive 
quarter of earnings beats. The data center segment posted revenue of $3.2 billion, up 38% YoY, 
while the gaming segment grew 12% to $1.4 billion.

CEO Lisa Su highlighted growing adoption of AMD's MI300 AI accelerators, which are competing 
directly with Nvidia in the burgeoning AI infrastructure market. "We're seeing tremendous 
traction with hyperscale customers deploying our AI solutions," Su said on the earnings call.

For the current quarter, AMD guided revenue of $7.0-7.4 billion, ahead of analyst expectations. 
Multiple investment firms upgraded their ratings following the results, with Jefferies citing 
"underappreciated growth potential in AI."
""".strip(),
            "author": "Financial Reporter",
            "sentiment_context": "earnings_beat"
        },
        {
            "source": "demo_openai_api",
            "topic": "AMD",
            "title": "AMD Faces Headwinds as PC Market Softens, Gaming Revenue Declines",
            "url": "https://example.com/amd3",
            "published_at": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=5)).isoformat(),
            "content": """
Advanced Micro Devices reported disappointing results in its Client segment as the global PC 
market continues to struggle. Revenue from client processors declined 25% year-over-year, 
missing expectations and raising concerns about consumer demand.

The gaming division also showed weakness, with revenue down 8% sequentially due to lower 
console chip sales and soft demand for discrete graphics cards. This comes as competitor 
Nvidia maintains dominance in the gaming GPU market with over 80% market share.

Industry analysts noted that while AMD's data center business remains strong, the consumer 
segments represent significant headwinds. "AMD is facing a two-sided market where enterprise 
is booming but consumer is hurting," said analyst Patrick Moorhead.

The company acknowledged the challenges, stating that it expects "continued softness in the 
PC market through at least the first half of 2025." AMD's stock declined 3.5% following the 
commentary, though some analysts view this as a buying opportunity for long-term investors 
focused on the data center growth story.
""".strip(),
            "author": "Market Analysis Team",
            "sentiment_context": "segment_weakness"
        },
        {
            "source": "demo_openai_api",
            "topic": "AMD",
            "title": "AMD Partners with Microsoft for Custom AI Chips, Stock Surges",
            "url": "https://example.com/amd4",
            "published_at": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=8)).isoformat(),
            "content": """
AMD announced a major partnership with Microsoft today to develop custom AI accelerator chips 
for Azure cloud services. The multi-year agreement represents a significant win for AMD as it 
competes against Nvidia in the AI chip market.

Under the partnership, AMD will design specialized processors optimized for Microsoft's AI 
workloads, including large language model training and inference. The deal is valued at over 
$2 billion according to sources familiar with the matter.

"This partnership validates our AI strategy and positions us as a key player in the AI 
infrastructure market," said AMD CEO Lisa Su. Microsoft's endorsement could help AMD gain 
traction with other hyperscale customers who have predominantly relied on Nvidia.

AMD shares surged 7.8% on the news, with analysts calling it a "game changer" for the 
company's AI ambitions. Bank of America raised its price target to $195, citing the partnership 
as evidence that AMD can capture meaningful AI chip market share over the next 2-3 years.
""".strip(),
            "author": "Tech Business Correspondent",
            "sentiment_context": "strategic_partnership"
        }
    ]
    
    # Nvidia Articles (5 articles)
    nvidia_articles = [
        {
            "source": "demo_openai_api",
            "topic": "NVIDIA",
            "title": "Nvidia Crushes Earnings as AI Chip Demand Remains Insatiable",
            "url": "https://example.com/nvidia1",
            "published_at": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=10)).isoformat(),
            "content": """
Nvidia reported blockbuster quarterly results that shattered analyst expectations, with revenue 
more than tripling year-over-year to $22.1 billion, driven by unprecedented demand for its AI 
chips. Data center revenue soared to $18.4 billion, up 279% from a year ago.

The company's H100 and H200 GPU accelerators remain in extremely high demand from cloud 
providers and enterprises deploying AI systems. "Supply remains tight despite our best efforts 
to increase production," said CEO Jensen Huang. "We're working with our partners to expand 
capacity, but demand continues to outstrip supply."

Earnings per share of $4.02 crushed the $3.37 consensus estimate, while gross margins expanded 
to 75.1% from 70.1% a year ago. Nvidia also announced a 10-for-1 stock split to make shares 
more accessible to individual investors.

The company guided next quarter revenue to $28 billion, well above the $26.4 billion consensus. 
Nvidia's stock jumped 12% in after-hours trading, pushing its market capitalization past 
$2 trillion. Multiple analysts raised price targets, with some now projecting $1,000+ per share.
""".strip(),
            "author": "Business Editor",
            "sentiment_context": "exceptional_earnings"
        },
        {
            "source": "demo_openai_api",
            "topic": "NVIDIA",
            "title": "Nvidia Announces New Blackwell Architecture, Next-Gen AI Superiority",
            "url": "https://example.com/nvidia2",
            "published_at": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=13)).isoformat(),
            "content": """
Nvidia unveiled its next-generation Blackwell GPU architecture today, promising up to 5x 
performance improvements for AI training and inference workloads. The new B100 and B200 chips 
represent the most significant advancement in GPU technology in years.

CEO Jensen Huang demonstrated the new architecture's capabilities at the company's GTC 
conference, showing how it can train GPT-4 scale models in weeks instead of months. "Blackwell 
will enable the next generation of AI breakthroughs," Huang stated to a packed audience.

The new chips feature 208 billion transistors and deliver up to 20 petaflops of FP4 performance 
for AI training. Major cloud providers including Amazon Web Services, Microsoft Azure, and 
Google Cloud have all committed to deploying Blackwell-based systems starting in late 2025.

Industry analysts were overwhelmingly positive, with Wedbush calling Blackwell "a quantum leap" 
that will "cement Nvidia's dominance in AI for years to come." Nvidia's competitive moat 
appears stronger than ever as it continues to outpace rivals AMD and Intel.
""".strip(),
            "author": "Technology Reporter",
            "sentiment_context": "product_innovation"
        },
        {
            "source": "demo_openai_api",
            "topic": "NVIDIA",
            "title": "Concerns Mount Over Nvidia's Valuation as Stock Hits Record Highs",
            "url": "https://example.com/nvidia3",
            "published_at": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=16)).isoformat(),
            "content": """
Nvidia's meteoric rise has some investors questioning whether the stock has run too far, 
too fast. Trading at over 40x forward earnings, the company's valuation has reached levels 
that worry even bullish analysts about potential downside risks.

"Nvidia is an incredible company with strong fundamentals, but at this valuation, there's 
limited room for error," said a portfolio manager at a major fund. "Any signs of AI demand 
cooling or competition intensifying could lead to significant multiple compression."

Some analysts have begun expressing concerns about market saturation in AI chips, noting that 
current spending levels may not be sustainable. Additionally, increased competition from AMD, 
Intel, and custom chips from cloud providers could erode Nvidia's market dominance over time.

Short interest in Nvidia has increased 15% over the past month, though it remains relatively 
low compared to overall float. A few bearish analysts have issued sell ratings, arguing that 
expectations have become "unrealistically optimistic" and that the stock is "priced for 
perfection."
""".strip(),
            "author": "Investment Analysis Desk",
            "sentiment_context": "valuation_concerns"
        },
        {
            "source": "demo_openai_api",
            "topic": "NVIDIA",
            "title": "Nvidia Expands AI Software Ecosystem, Launches New Developer Tools",
            "url": "https://example.com/nvidia4",
            "published_at": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=19)).isoformat(),
            "content": """
Nvidia announced a comprehensive expansion of its AI software platform today, launching new 
developer tools and frameworks designed to make AI deployment easier and more efficient. The 
NIM (Nvidia Inference Microservices) platform enables developers to deploy optimized AI models 
with just a few lines of code.

The company also unveiled partnerships with major software companies including SAP, ServiceNow, 
and Salesforce to integrate Nvidia's AI capabilities into enterprise applications. This 
software-focused strategy helps create stickiness and reduces the risk of customers switching 
to competing hardware.

"We're not just selling chips, we're building the complete AI infrastructure stack," said 
Nvidia's VP of Enterprise Software. The company's CUDA platform remains the industry standard 
for GPU programming, giving Nvidia a significant ecosystem advantage over competitors.

Analysts view the software expansion positively, as it diversifies revenue streams and 
increases customer lock-in. Raymond James noted that "Nvidia's software moat is underappreciated" 
and raised its price target citing the "stickiness" of the CUDA ecosystem.
""".strip(),
            "author": "Enterprise Tech Correspondent",
            "sentiment_context": "ecosystem_expansion"
        },
        {
            "source": "demo_openai_api",
            "topic": "NVIDIA",
            "title": "Nvidia Faces Export Restrictions to China, Analysts Assess Impact",
            "url": "https://example.com/nvidia5",
            "published_at": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=22)).isoformat(),
            "content": """
The U.S. government announced expanded export controls affecting Nvidia's high-performance 
AI chips to China, restricting sales of the company's most advanced GPUs to the region. The 
new rules target chips capable of certain performance levels, affecting Nvidia's A100, H100, 
and future products.

China represented approximately 20-25% of Nvidia's data center revenue, making these 
restrictions material to near-term growth. The company acknowledged it is developing 
China-specific chips that comply with the new regulations, but these will have significantly 
reduced capabilities and margins.

"While we're disappointed by these restrictions, we believe strong global demand outside 
China will offset most of the impact," Nvidia stated. However, some analysts lowered estimates, 
with Bernstein cutting its revenue forecast by 4-6% for the next fiscal year.

The restrictions also raise concerns about potential retaliation or further escalation of 
tech trade tensions. Despite the headwinds, most analysts remain positive on Nvidia's long-term 
prospects given its leadership position and strong demand in other regions.
""".strip(),
            "author": "Policy and Markets Reporter",
            "sentiment_context": "regulatory_headwind"
        }
    ]
    
    # Broadcom Articles (5 articles)
    broadcom_articles = [
        {
            "source": "demo_openai_api",
            "topic": "AVGO",
            "title": "Broadcom Completes VMware Acquisition, Creates Software Powerhouse",
            "url": "https://example.com/broadcom1",
            "published_at": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).isoformat(),
            "content": """
Broadcom officially closed its $69 billion acquisition of VMware today, creating one of the 
world's largest infrastructure technology companies. The deal combines Broadcom's semiconductor 
and enterprise software businesses with VMware's leading virtualization and cloud platforms.

CEO Hock Tan outlined plans to aggressively cross-sell VMware's products to Broadcom's extensive 
enterprise customer base. "This acquisition transforms Broadcom into an infrastructure technology 
leader with $50 billion in annual revenue," Tan said.

The company expects to realize $3 billion in cost synergies within three years through 
operational efficiencies and restructuring. Broadcom also announced plans to significantly 
increase R&D spending on VMware's core products while discontinuing non-strategic offerings.

Wall Street analysts are divided on the deal, with bulls citing revenue synergies and cash 
flow generation, while bears worry about integration risks and potential customer attrition. 
Broadcom's stock rose 2.5% on the completion announcement, though some VMware customers have 
expressed concerns about future pricing and product direction.
""".strip(),
            "author": "M&A Analysis Team",
            "sentiment_context": "major_acquisition"
        },
        {
            "source": "demo_openai_api",
            "topic": "AVGO",
            "title": "Broadcom Reports Strong AI Chip Sales, Diversification Paying Off",
            "url": "https://example.com/broadcom2",
            "published_at": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1, hours=3)).isoformat(),
            "content": """
Broadcom reported quarterly earnings that beat expectations, with particular strength in its 
custom AI accelerator business. Revenue from AI chips grew 87% year-over-year to $2.1 billion, 
as hyperscale customers increasingly deploy Broadcom's custom solutions alongside Nvidia GPUs.

The company's diversified business model proved resilient, with semiconductor sales up 11% 
while infrastructure software revenue grew 8%. CEO Hock Tan highlighted wins with Google and 
Meta for custom AI chip designs, positioning Broadcom as a key alternative to merchant silicon.

"Our custom AI accelerators offer customers optimized performance for their specific workloads," 
Tan explained. "We're seeing strong demand from cloud providers looking to reduce costs and 
improve efficiency beyond what off-the-shelf GPUs can provide."

Earnings per share of $10.54 exceeded the $10.32 estimate, while gross margins held steady 
at 68%. The company raised full-year guidance, citing momentum in AI and networking chips. 
Analysts praised Broadcom's execution and diversified revenue streams, with several raising 
price targets.
""".strip(),
            "author": "Semiconductor Industry Reporter",
            "sentiment_context": "earnings_strength"
        },
        {
            "source": "demo_openai_api",
            "topic": "AVGO",
            "title": "Broadcom Faces VMware Customer Backlash Over Licensing Changes",
            "url": "https://example.com/broadcom3",
            "published_at": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1, hours=6)).isoformat(),
            "content": """
Broadcom is facing growing criticism from VMware customers following significant changes to 
the company's licensing and pricing model. The new subscription-based approach has led to 
price increases of 100-300% for some customers, sparking backlash and threats of migration 
to alternative platforms.

Multiple large enterprises have publicly announced plans to evaluate competing solutions from 
Microsoft Azure, Amazon AWS, and open-source alternatives. "The price increases are simply 
untenable," said an IT director at a Fortune 500 company who requested anonymity.

Industry analysts warn that the aggressive monetization strategy could backfire, potentially 
driving away customers and damaging VMware's market position. Gartner noted increased inquiries 
about VMware alternatives, suggesting "meaningful customer churn risk."

Broadcom defended the changes, stating that the new model provides better value through 
bundled offerings and simplified licensing. However, the company's stock declined 4.2% as 
investors worried about potential revenue headwinds from customer defections. Some analysts 
have lowered their VMware revenue estimates by 10-15% for the next fiscal year.
""".strip(),
            "author": "Enterprise Software Watch",
            "sentiment_context": "customer_backlash"
        },
        {
            "source": "demo_openai_api",
            "topic": "AVGO",
            "title": "Broadcom Announces Record Dividend Increase, Returns Cash to Shareholders",
            "url": "https://example.com/broadcom4",
            "published_at": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1, hours=9)).isoformat(),
            "content": """
Broadcom announced a 14% increase to its quarterly dividend, marking the company's 13th 
consecutive year of dividend growth. The new quarterly dividend of $5.25 per share yields 
approximately 2.1% at current stock prices, making Broadcom one of the highest-yielding 
semiconductor stocks.

CEO Hock Tan reaffirmed the company's commitment to returning at least 50% of free cash flow 
to shareholders through dividends and buybacks. "We generate tremendous cash flow from our 
diversified business model, and we're committed to sharing that with our investors," Tan stated.

The company also authorized an additional $10 billion stock buyback program, adding to the 
$4 billion remaining under the existing authorization. Free cash flow for the quarter was 
$4.8 billion, up 18% year-over-year, driven by strong margins and efficient working capital 
management.

Income-focused investors and analysts praised the announcement, with several firms reiterating 
buy ratings based on Broadcom's "attractive yield and sustainable dividend growth." The stock 
rose 1.8% following the announcement, with analysts at Morgan Stanley calling Broadcom "a 
compelling total return story."
""".strip(),
            "author": "Dividend & Income Desk",
            "sentiment_context": "shareholder_returns"
        },
        {
            "source": "demo_openai_api",
            "topic": "AVGO",
            "title": "Broadcom Secures Major 5G Infrastructure Deals, Telecom Growth Accelerates",
            "url": "https://example.com/broadcom5",
            "published_at": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1, hours=12)).isoformat(),
            "content": """
Broadcom announced significant new design wins for its 5G infrastructure chips with major 
telecom equipment makers, positioning the company to benefit from the ongoing global 5G 
network buildout. The multi-year deals are valued at over $1.5 billion in aggregate revenue.

The company's networking chips will be used in next-generation 5G base stations and edge 
computing equipment deployed by carriers worldwide. "5G infrastructure remains a significant 
growth opportunity as carriers upgrade their networks," said Broadcom's President of Semiconductor 
Solutions.

Broadcom's diversified semiconductor portfolio includes leading positions in wireless, networking, 
and broadband chips for both enterprise and telecom applications. This diversification has 
helped buffer the company from cyclical downturns in any single market.

Analysts were positive on the news, with KeyBanc noting that "5G infrastructure deployments 
are accelerating in Asia and Europe, providing a multi-year tailwind for Broadcom's wireless 
business." The deals also demonstrate Broadcom's ability to compete effectively with rivals 
like Qualcomm and MediaTek in the 5G chip market.
""".strip(),
            "author": "Telecom Technology Reporter",
            "sentiment_context": "infrastructure_wins"
        }
    ]
    
    # Combine all articles
    all_articles = []
    
    # Save AMD articles
    amd_dir = base_dir / "demo_openai_api" / "AMD"
    amd_dir.mkdir(parents=True, exist_ok=True)
    for i, article in enumerate(amd_articles, 1):
        filename = f"00{i}_amd_article.json"
        filepath = amd_dir / filename
        with open(filepath, "w") as f:
            json.dump(article, f, indent=2)
        all_articles.append((filepath, article))
        print(f"✓ Created AMD article {i}/4: {article['title'][:60]}...")
    
    # Save Nvidia articles
    nvidia_dir = base_dir / "demo_openai_api" / "NVIDIA"
    nvidia_dir.mkdir(parents=True, exist_ok=True)
    for i, article in enumerate(nvidia_articles, 1):
        filename = f"00{i}_nvidia_article.json"
        filepath = nvidia_dir / filename
        with open(filepath, "w") as f:
            json.dump(article, f, indent=2)
        all_articles.append((filepath, article))
        print(f"✓ Created Nvidia article {i}/5: {article['title'][:60]}...")
    
    # Save Broadcom articles
    broadcom_dir = base_dir / "demo_openai_api" / "AVGO"
    broadcom_dir.mkdir(parents=True, exist_ok=True)
    for i, article in enumerate(broadcom_articles, 1):
        filename = f"00{i}_broadcom_article.json"
        filepath = broadcom_dir / filename
        with open(filepath, "w") as f:
            json.dump(article, f, indent=2)
        all_articles.append((filepath, article))
        print(f"✓ Created Broadcom article {i}/5: {article['title'][:60]}...")
    
    print(f"\nTotal articles created: {len(all_articles)}")
    return all_articles


def analyze_with_openai(articles, prompt_template, api_key, model="gpt-4o-mini"):
    """Analyze articles using the OpenAI API."""
    print("\n" + "=" * 70)
    print("ANALYZING ARTICLES WITH OPENAI API")
    print("=" * 70)
    print(f"Model: {model}")
    print(f"Total articles to analyze: {len(articles)}\n")
    
    results = []
    llm_scores_dir = Path(__file__).parent.parent / "demo_output_openai" / "llm_scores"
    
    for i, (article_file, article) in enumerate(articles, 1):
        print(f"[{i}/{len(articles)}] Processing: {article['title'][:60]}...")
        print(f"             Topic: {article['topic']}")
        
        # Format prompt (without market context for this demo)
        full_prompt = format_prompt(prompt_template, article, "")
        
        # Call OpenAI API
        print("             Calling OpenAI API...", end=" ", flush=True)
        response_text = call_openai_api(full_prompt, api_key, model)
        
        if response_text is None:
            print("✗ Failed")
            continue
        
        print("✓ Success")
        
        # Parse response
        score, explanation = parse_llm_response(response_text)
        
        if score is not None:
            print(f"             Score: {score:+.2f}")
            print(f"             Explanation: {explanation[:70]}...")
            
            # Save score
            save_llm_score(article_file, article, score, explanation, llm_scores_dir, model)
            results.append({
                "topic": article["topic"],
                "title": article["title"],
                "score": score,
                "explanation": explanation
            })
        else:
            print("             ✗ Failed to parse response")
        
        print()
    
    return results


def show_results(results):
    """Display analysis results."""
    print("=" * 70)
    print("ANALYSIS RESULTS")
    print("=" * 70)
    
    if not results:
        print("\nNo results to display.")
        return
    
    print(f"\nTotal articles analyzed: {len(results)}")
    
    # Group by topic
    by_topic = {}
    for result in results:
        topic = result["topic"]
        if topic not in by_topic:
            by_topic[topic] = []
        by_topic[topic].append(result)
    
    print("\n" + "-" * 70)
    for topic in sorted(by_topic.keys()):
        articles = by_topic[topic]
        avg_score = sum(a["score"] for a in articles) / len(articles)
        
        print(f"\n{topic}: {len(articles)} articles, Average Score: {avg_score:+.2f}")
        print("-" * 70)
        
        for article in articles:
            score_indicator = "↑" if article["score"] > 0 else "↓" if article["score"] < 0 else "→"
            title = article["title"][:55] + "..." if len(article["title"]) > 58 else article["title"]
            print(f"  {score_indicator} {article['score']:+6.2f}  {title}")
            explanation = article["explanation"][:65] + "..." if len(article["explanation"]) > 65 else article["explanation"]
            print(f"             └─ {explanation}")
    
    print("\n" + "=" * 70)
    overall_avg = sum(r["score"] for r in results) / len(results)
    print(f"Overall average sentiment: {overall_avg:+.2f}")
    print("=" * 70)


def main():
    """Run the OpenAI API demonstration."""
    print("\n" + "=" * 70)
    print("VUTS - OPENAI API SENTIMENT ANALYSIS DEMO")
    print("=" * 70)
    print("\nThis demo generates articles about AMD, Nvidia, and Broadcom,")
    print("then uses the OpenAI API to analyze sentiment as VUTS does.")
    print()
    
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set!")
        print("\nTo run this demo, you need an OpenAI API key:")
        print("  1. Get an API key from https://platform.openai.com/api-keys")
        print("  2. Export it: export OPENAI_API_KEY='your-api-key'")
        print("  3. Run this script again")
        print("\nEstimated cost: ~$0.01 (less than 2 cents for all articles)")
        return 1
    
    print(f"✓ OpenAI API key found")
    print("✓ Estimated cost: ~$0.01 for all articles\n")
    
    # Setup
    demo_dir = Path(__file__).parent.parent / "demo_output_openai"
    demo_dir.mkdir(exist_ok=True)
    
    # Load prompt template
    prompt_file = Path(__file__).parent.parent / "src" / "llm" / "sentiment_prompt.txt"
    if not prompt_file.exists():
        print(f"ERROR: Prompt template not found at {prompt_file}")
        return 1
    
    prompt_template = load_prompt_template(prompt_file)
    print(f"✓ Loaded prompt template from {prompt_file.name}\n")
    
    # Create demo articles
    articles = create_demo_articles(demo_dir)
    
    # Ask for confirmation before calling API
    print("\n" + "=" * 70)
    print("READY TO CALL OPENAI API")
    print("=" * 70)
    print(f"Articles to analyze: {len(articles)}")
    print(f"Estimated tokens: ~{len(articles) * 1500} tokens")
    print(f"Estimated cost: ~$0.{len(articles) // 2:02d} USD")
    print("\nPress Enter to proceed or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        return 0
    
    # Analyze with OpenAI
    results = analyze_with_openai(articles, prompt_template, api_key)
    
    # Show results
    show_results(results)
    
    print(f"\nDemo files saved to: {demo_dir}")
    print(f"Sentiment scores saved to: {demo_dir / 'llm_scores'}")
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    exit(main())
