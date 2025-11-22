#!/usr/bin/env python3
"""
"Real World" Demo: Large-scale demonstration with 12 companies.

This demo creates a comprehensive dataset showcasing how the VUTS system works
at scale with realistic scenarios. It includes:
- 12 companies across different sectors
- 15-23 articles per company (with variance)
- Different writing styles and lengths
- Diverse sentiments (positive, negative, neutral)
- Realistic scenarios (not all true, just for demonstration)

No API keys required for the basic demo (uses mock scoring).
Optional: Set OPENAI_API_KEY to use real sentiment analysis.
"""

import json
import datetime
import random
import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm.sentiment_analyzer import (
    load_prompt_template,
    format_prompt,
    parse_llm_response,
    save_llm_score
)

# Check if OpenAI API is available
try:
    from llm.sentiment_analyzer import call_openai_api
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# Company information
COMPANIES = [
    {
        "symbol": "TSLA",
        "name": "Tesla Inc.",
        "sector": "Automotive/Electric Vehicles",
        "description": "Leading electric vehicle and clean energy company"
    },
    {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "sector": "Technology/Consumer Electronics",
        "description": "Technology company known for iPhone, Mac, and services"
    },
    {
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "sector": "E-Commerce/Cloud Computing",
        "description": "E-commerce and cloud computing giant"
    },
    {
        "symbol": "GOOGL",
        "name": "Alphabet Inc.",
        "sector": "Technology/Internet Services",
        "description": "Parent company of Google and various tech ventures"
    },
    {
        "symbol": "MSFT",
        "name": "Microsoft Corporation",
        "sector": "Technology/Software",
        "description": "Software giant and cloud computing leader"
    },
    {
        "symbol": "META",
        "name": "Meta Platforms Inc.",
        "sector": "Social Media/Technology",
        "description": "Social media and virtual reality company"
    },
    {
        "symbol": "NVDA",
        "name": "NVIDIA Corporation",
        "sector": "Semiconductors/AI",
        "description": "AI and graphics processing leader"
    },
    {
        "symbol": "JPM",
        "name": "JPMorgan Chase & Co.",
        "sector": "Banking/Financial Services",
        "description": "Major multinational investment bank"
    },
    {
        "symbol": "DIS",
        "name": "The Walt Disney Company",
        "sector": "Entertainment/Media",
        "description": "Entertainment and media conglomerate"
    },
    {
        "symbol": "BA",
        "name": "The Boeing Company",
        "sector": "Aerospace/Defense",
        "description": "Aerospace manufacturer and defense contractor"
    },
    {
        "symbol": "NFLX",
        "name": "Netflix Inc.",
        "sector": "Streaming/Entertainment",
        "description": "Streaming entertainment service provider"
    },
    {
        "symbol": "AMD",
        "name": "Advanced Micro Devices Inc.",
        "sector": "Semiconductors",
        "description": "Semiconductor company competing in CPU and GPU markets"
    }
]


# Article templates and content generators
def generate_earnings_beat_article(company: Dict, positive: bool = True) -> Dict:
    """Generate an earnings beat/miss article."""
    if positive:
        beat_pct = random.choice([5, 8, 12, 15, 18, 20])
        eps_actual = round(random.uniform(1.5, 3.5), 2)
        eps_expected = round(eps_actual * (1 - beat_pct/100), 2)
        revenue = round(random.uniform(15, 45), 1)
        yoy_growth = random.choice([12, 15, 18, 22, 25, 28])
        
        title = f"{company['name']} Crushes Q{random.randint(1,4)} Earnings, Beats Expectations by {beat_pct}%"
        content = f"""{company['name']} reported outstanding quarterly results that exceeded Wall Street expectations across all metrics. The {company['sector']} leader posted earnings per share of ${eps_actual}, crushing analyst estimates of ${eps_expected} by {beat_pct}%.

Revenue came in at ${revenue} billion, representing {yoy_growth}% year-over-year growth and comfortably above the consensus estimate of ${revenue * 0.95:.1f} billion. The strong performance was driven by robust demand across all segments and improved operational efficiency.

CEO commentary emphasized the company's strong competitive position and optimistic outlook for the coming quarters. "We're executing on all fronts and seeing tremendous momentum in our business," the CEO stated during the earnings call. "Our investments in innovation are paying off, and we're well-positioned for continued growth."

Multiple analysts raised their price targets following the results, with several upgrading their ratings. Morgan Stanley cited "exceptional execution and market share gains" as key drivers. The company also announced a {random.choice([8, 10, 12, 15])}% dividend increase, rewarding shareholders.

Looking ahead, management provided guidance that exceeded analyst expectations, signaling confidence in sustained momentum. The stock surged {random.choice([5, 7, 9, 11, 13])}% in after-hours trading as investors celebrated the strong results and positive outlook."""
        
        sentiment_hint = random.uniform(6.0, 8.5)
        
    else:
        miss_pct = random.choice([5, 8, 10, 12, 15])
        eps_actual = round(random.uniform(0.8, 2.2), 2)
        eps_expected = round(eps_actual * (1 + miss_pct/100), 2)
        revenue = round(random.uniform(12, 35), 1)
        yoy_decline = random.choice([-3, -5, -8, -10])
        
        title = f"{company['name']} Misses Earnings Estimates, Revenue Down {abs(yoy_decline)}% Year-Over-Year"
        content = f"""{company['name']} reported disappointing quarterly results that fell short of analyst expectations. The company posted earnings per share of ${eps_actual}, missing consensus estimates of ${eps_expected} by {miss_pct}%. 

Revenue declined {abs(yoy_decline)}% year-over-year to ${revenue} billion, below the expected ${revenue * 1.08:.1f} billion. The weak performance reflected challenging market conditions, increased competition, and operational headwinds that the company acknowledged in its earnings release.

"While we're disappointed with these results, we're taking decisive action to improve performance," management stated. The company cited macro economic pressures, softening demand in key markets, and margin compression as primary challenges.

Several analysts downgraded the stock following the results, expressing concerns about the company's ability to return to growth. Jefferies lowered its price target by {random.choice([15, 20, 25])}%, citing "structural headwinds and execution issues." Market sentiment turned negative as investors questioned the company's strategic direction.

Management's guidance for next quarter came in below expectations, further dampening investor enthusiasm. The stock fell {random.choice([6, 8, 11, 14])}% in after-hours trading, with concerns mounting about near-term profitability and competitive positioning."""
        
        sentiment_hint = random.uniform(-7.5, -4.5)
    
    return {
        "title": title,
        "content": content.strip(),
        "sentiment_context": "earnings_beat" if positive else "earnings_miss",
        "expected_score": sentiment_hint
    }


def generate_product_announcement(company: Dict, positive: bool = True) -> Dict:
    """Generate a product announcement article."""
    if positive:
        product_name = random.choice([
            "Next-Generation Platform", "Revolutionary Device", "Advanced System",
            "Breakthrough Technology", "Innovation Suite", "Premium Product Line"
        ])
        
        improvement_pct = random.choice([30, 40, 50, 60, 75, 100])
        
        title = f"{company['name']} Unveils {product_name}, Industry Experts Impressed"
        content = f"""{company['name']} today announced its latest innovation in {company['sector'].split('/')[0].lower()}, the {product_name}, receiving widespread praise from industry analysts and early reviewers. The new offering represents a significant leap forward in capabilities and design.

The {product_name} delivers up to {improvement_pct}% better performance compared to the previous generation, while also improving energy efficiency and reducing costs. Early benchmark tests show the product outperforming competitor offerings across key metrics.

"This is a game-changer for the industry," said the company's Chief Technology Officer. "We've reimagined what's possible and delivered a product that sets a new standard." The announcement comes after years of research and development, with the company investing heavily in innovation.

Industry analysts responded positively, with several noting that the {product_name} could strengthen {company['name']}'s competitive position and drive market share gains. "This addresses a clear market need and showcases {company['name']}'s innovation leadership," commented a leading analyst at Gartner.

Pre-orders opened immediately following the announcement, with initial customer response described as "extremely strong." The company expects the {product_name} to contribute meaningfully to revenue starting in the current quarter, with full availability planned for next month."""
        
        sentiment_hint = random.uniform(5.0, 7.5)
        
    else:
        product_name = random.choice([
            "Latest Product", "Updated Platform", "New Device",
            "Redesigned System", "Next Release"
        ])
        
        title = f"{company['name']} Product Launch Falls Flat, Critics Point to Lack of Innovation"
        content = f"""{company['name']}'s much-anticipated {product_name} launched today to mixed reviews, with critics noting incremental improvements rather than the revolutionary changes that were promised. Early user feedback has been lukewarm at best.

Tech reviewers pointed out that the {product_name} offers only marginal improvements over the previous generation, while competitor products have leapfrogged ahead in key features. "This feels like a missed opportunity," wrote a prominent tech journalist. "The market was expecting more innovation."

Pre-orders have been disappointing, coming in well below analyst expectations. Several retail partners reported weak initial interest, raising questions about demand and the product's market positioning. The lackluster response has surprised company executives who had high hopes for the launch.

Industry analysts expressed concern about {company['name']}'s ability to compete effectively in an increasingly crowded market. Some have lowered revenue estimates for the product line, citing "uninspiring features and questionable pricing."

The company defended the product, emphasizing its reliability and ecosystem integration. However, the negative reception has raised doubts about the product strategy and innovation pipeline. Investors reacted negatively, with shares declining {random.choice([3, 4, 5])}% following the launch event."""
        
        sentiment_hint = random.uniform(-5.5, -3.0)
    
    return {
        "title": title,
        "content": content.strip(),
        "sentiment_context": "product_positive" if positive else "product_negative",
        "expected_score": sentiment_hint
    }


def generate_partnership_article(company: Dict, positive: bool = True) -> Dict:
    """Generate a partnership/strategic deal article."""
    if positive:
        partner = random.choice([
            "Major Technology Leader", "Global Industry Giant", "Fortune 100 Company",
            "Leading Enterprise Partner", "International Corporation"
        ])
        deal_value = random.choice([500, 750, 1000, 1500, 2000, 3000])
        
        title = f"{company['name']} Announces Strategic Partnership with {partner}"
        content = f"""{company['name']} unveiled a major strategic partnership with {partner} today, valued at over ${deal_value} million over the next {random.choice([3, 4, 5])} years. The collaboration aims to accelerate innovation and expand market reach in {company['sector'].split('/')[0].lower()}.

Under the agreement, both companies will jointly develop next-generation solutions and share technology resources. The partnership is expected to create significant synergies, with combined expertise driving faster time-to-market for new offerings.

"This partnership brings together two industry leaders with complementary strengths," said {company['name']}'s CEO. "Together, we can deliver greater value to customers and accelerate our growth trajectory." The announcement was met with enthusiasm from both companies' stakeholder bases.

Financial analysts view the deal positively, noting it expands {company['name']}'s addressable market and provides access to {partner}'s extensive customer base. Raymond James raised its price target, calling the partnership "strategically smart and financially accretive."

The companies plan to launch the first joint products within {random.choice([6, 9, 12])} months, with several additional initiatives in development. Early customer feedback suggests strong interest in the combined offerings, positioning both companies for growth."""
        
        sentiment_hint = random.uniform(4.5, 7.0)
        
    else:
        partner = random.choice([
            "Struggling Competitor", "Financially Troubled Firm", "Controversial Partner"
        ])
        
        title = f"{company['name']} Partnership Deal Raises Eyebrows Among Investors"
        content = f"""{company['name']} announced a partnership with {partner} today, but investors and analysts questioned the strategic rationale and potential risks. The deal has raised concerns about dilution of focus and potential exposure to the partner's challenges.

Details of the partnership remain vague, with neither company providing clear metrics for success or specific timelines for deliverables. Industry observers noted that {partner} has faced significant headwinds recently, raising questions about their ability to contribute meaningfully.

"We're struggling to understand the strategic logic here," commented an analyst at a major investment bank. "This partnership doesn't appear to play to {company['name']}'s strengths and may distract from core priorities."

Several shareholders expressed disappointment with the announcement, with some calling for more transparency about the terms and expected benefits. The lack of financial details has fueled speculation about potential risks and opportunity costs.

{company['name']}'s stock declined {random.choice([2, 3, 4])}% following the announcement, reflecting market skepticism. Analysts have adopted a wait-and-see approach, though several have lowered near-term estimates citing integration risks and potential distraction from core business initiatives."""
        
        sentiment_hint = random.uniform(-4.5, -2.0)
    
    return {
        "title": title,
        "content": content.strip(),
        "sentiment_context": "partnership_positive" if positive else "partnership_negative",
        "expected_score": sentiment_hint
    }


def generate_regulatory_article(company: Dict, positive: bool = True) -> Dict:
    """Generate a regulatory/legal article."""
    if positive:
        approval_type = random.choice([
            "Regulatory Approval", "Government Clearance", "Legal Victory",
            "Favorable Ruling", "Compliance Certification"
        ])
        
        title = f"{company['name']} Secures {approval_type}, Clearing Path for Expansion"
        content = f"""{company['name']} announced today that it has received {approval_type.lower()} from regulatory authorities, removing a significant obstacle to its growth plans. The decision clears the way for the company to proceed with strategic initiatives that were previously on hold.

The approval came after an extensive review process lasting {random.choice([6, 8, 12, 18])} months. {company['name']} worked closely with regulators to address concerns and demonstrate compliance with all requirements. "This is a major milestone that validates our approach," stated the company's Chief Legal Officer.

Industry experts view the decision as a significant win for {company['name']}, potentially unlocking new market opportunities and revenue streams. The favorable regulatory environment is expected to provide a competitive advantage and accelerate the company's strategic roadmap.

Financial analysts welcomed the news, with several raising price targets based on improved growth prospects. "This removes a major overhang and de-risks the growth story," noted an analyst at Wells Fargo. The company can now focus on execution without regulatory uncertainty.

Shareholders responded positively, driving the stock up {random.choice([4, 6, 7, 9])}% in morning trading. Management indicated that it will provide updated guidance incorporating the new opportunities enabled by the regulatory approval."""
        
        sentiment_hint = random.uniform(4.0, 6.5)
        
    else:
        issue_type = random.choice([
            "Regulatory Investigation", "Antitrust Probe", "Compliance Violation",
            "Legal Challenge", "Government Inquiry"
        ])
        potential_fine = random.choice([100, 250, 500, 750, 1000])
        
        title = f"{company['name']} Faces {issue_type}, Potential Fines Could Reach ${potential_fine}M"
        content = f"""{company['name']} disclosed today that it is subject to a {issue_type.lower()} by regulatory authorities, creating uncertainty about potential penalties and operational impacts. The investigation focuses on alleged violations of industry regulations and could result in substantial fines.

According to the company's filing, regulators are examining practices dating back {random.choice([2, 3, 4])} years. {company['name']} stated it is "cooperating fully" with the investigation but did not provide details about specific allegations or potential exposure.

Legal experts suggest the investigation could take {random.choice([12, 18, 24])} months to resolve, creating an overhang on the stock. Potential penalties could range from ${potential_fine // 2}M to ${potential_fine}M, plus mandated changes to business practices that may impact profitability.

Industry analysts expressed concern about the regulatory risk and potential reputational damage. "This adds significant uncertainty to the investment thesis," commented an analyst at Bernstein. Several firms have placed their ratings under review pending resolution of the matter.

The company's stock fell {random.choice([5, 7, 9, 12])}% on the news, with investors repricing shares to reflect regulatory risk. Management attempted to reassure stakeholders but acknowledged the investigation will be a focus area requiring significant resources and attention."""
        
        sentiment_hint = random.uniform(-7.0, -4.0)
    
    return {
        "title": title,
        "content": content.strip(),
        "sentiment_context": "regulatory_positive" if positive else "regulatory_negative",
        "expected_score": sentiment_hint
    }


def generate_leadership_article(company: Dict, positive: bool = True) -> Dict:
    """Generate a leadership change article."""
    if positive:
        new_role = random.choice(["Chief Technology Officer", "Chief Operating Officer", 
                                   "President of Global Operations", "Head of Innovation"])
        executive_bg = random.choice([
            "veteran technology executive", "former industry leader",
            "renowned innovator", "proven strategic leader"
        ])
        
        title = f"{company['name']} Appoints Industry Veteran as {new_role}"
        content = f"""{company['name']} announced the appointment of a highly respected {executive_bg} to the position of {new_role}, strengthening its leadership team as it pursues ambitious growth plans.

The new executive brings {random.choice([15, 20, 25])} years of experience in {company['sector'].split('/')[0].lower()} and has a track record of driving innovation and operational excellence at previous companies. "We're thrilled to have such exceptional talent joining our team," said {company['name']}'s CEO.

The appointment was welcomed by analysts and investors who view it as evidence of {company['name']}'s commitment to execution and strategic focus. The new {new_role} will be responsible for key initiatives that are central to the company's growth strategy.

Industry observers noted that attracting top-tier talent demonstrates {company['name']}'s appeal as an employer and confidence in its future prospects. "This is exactly the kind of leadership depth that will drive long-term value creation," commented an analyst at Goldman Sachs.

The new executive is expected to start in {random.choice([30, 60, 90])} days and will report directly to the CEO. {company['name']}'s shares rose {random.choice([2, 3, 4])}% on the announcement as investors welcomed the leadership addition."""
        
        sentiment_hint = random.uniform(2.5, 5.0)
        
    else:
        departing_role = random.choice(["Chief Executive Officer", "Chief Financial Officer",
                                        "Chief Technology Officer", "President"])
        reason = random.choice([
            "unexpected resignation", "abrupt departure", 
            "announced exit", "sudden stepping down"
        ])
        
        title = f"{company['name']} {departing_role} Announces {reason.title()}"
        content = f"""{company['name']} disclosed that its {departing_role} has announced {reason}, creating uncertainty about leadership continuity during a critical period for the company. The departure was characterized as {random.choice(['sudden', 'unexpected', 'surprising'])}, with limited explanation provided.

The company stated it has initiated a search for a replacement and appointed an interim leader, but provided no timeline for permanent succession. Industry analysts expressed concern about the leadership void during a time when {company['name']} faces significant strategic and operational challenges.

"Leadership stability is crucial, and this departure raises questions about internal dynamics and strategic direction," noted an analyst who covers the company. The {reason} comes amid {random.choice(['disappointing financial results', 'strategic questions', 'operational challenges'])}.

Several major shareholders have reportedly expressed concern to the board about succession planning and governance. The uncertainty around leadership has overshadowed other company developments and created a distraction for the organization.

{company['name']}'s stock declined {random.choice([4, 6, 8, 10])}% following the announcement, with investors worried about execution risk and potential strategic shifts under new leadership. The company attempted to project stability but acknowledged the transition will require careful management."""
        
        sentiment_hint = random.uniform(-6.0, -3.5)
    
    return {
        "title": title,
        "content": content.strip(),
        "sentiment_context": "leadership_positive" if positive else "leadership_negative",
        "expected_score": sentiment_hint
    }


def generate_market_analysis_article(company: Dict, positive: bool = True) -> Dict:
    """Generate a market analysis/analyst rating article."""
    if positive:
        firm = random.choice(["Goldman Sachs", "Morgan Stanley", "JP Morgan", 
                             "Bank of America", "Wells Fargo", "Barclays"])
        old_target = random.randint(120, 280)
        new_target = int(old_target * random.uniform(1.15, 1.35))
        
        title = f"{firm} Upgrades {company['name']} to Buy, Raises Price Target to ${new_target}"
        content = f"""{firm} analyst upgraded {company['name']} to Buy from Neutral today, citing improved fundamentals and attractive valuation. The firm also raised its price target to ${new_target} from ${old_target}, representing {int((new_target/old_target - 1)*100)}% upside from current levels.

The upgrade reflects growing conviction in {company['name']}'s ability to execute on its strategic initiatives and capture market share in {company['sector'].split('/')[0].lower()}. The analyst highlighted several positive catalysts including {random.choice(['accelerating revenue growth', 'margin expansion', 'market share gains', 'innovation pipeline'])}.

"We believe {company['name']} is well-positioned to outperform over the next 12-18 months," the analyst wrote in a research note. "The risk/reward profile has improved significantly, and we see multiple paths to upside from current levels."

The positive call comes as {company['name']} has demonstrated {random.choice(['consistent execution', 'strong momentum', 'competitive advantages'])}. {firm} joins a growing number of firms taking a more constructive view on the stock.

Following the upgrade, {company['name']}'s shares rose {random.choice([3, 4, 5, 6])}%, with trading volume elevated. The stock has now been upgraded by {random.choice([3, 4, 5])} firms in the past month, reflecting improving sentiment among the analyst community."""
        
        sentiment_hint = random.uniform(3.5, 6.0)
        
    else:
        firm = random.choice(["Bernstein", "Redburn", "New Street Research", 
                             "MoffettNathanson", "Evercore ISI"])
        old_target = random.randint(180, 320)
        new_target = int(old_target * random.uniform(0.65, 0.85))
        
        title = f"{firm} Downgrades {company['name']}, Cuts Price Target on Multiple Concerns"
        content = f"""{firm} downgraded {company['name']} to Underperform today, slashing its price target to ${new_target} from ${old_target}, a {int((1 - new_target/old_target)*100)}% reduction. The firm cited deteriorating fundamentals, competitive pressures, and valuation concerns.

The downgrade reflects growing skepticism about {company['name']}'s growth prospects and ability to defend market position. The analyst highlighted {random.choice(['slowing revenue growth', 'margin compression', 'market share losses', 'execution issues'])} as key concerns.

"We see limited upside from current levels and growing downside risks," the analyst wrote. "Multiple headwinds are converging, and we believe consensus estimates remain too optimistic." {firm} now has one of the most bearish views on Wall Street regarding {company['name']}.

The negative call comes amid {random.choice(['disappointing financial trends', 'increasing competition', 'strategic questions'])}. Several other firms have also adopted a more cautious stance recently, though {firm}'s downgrade is the most aggressive.

{company['name']}'s shares fell {random.choice([4, 5, 6, 8])}% following the downgrade, pressured by the negative analyst commentary. The stock has now been downgraded by {random.choice([2, 3, 4])} firms in recent weeks, contributing to negative momentum."""
        
        sentiment_hint = random.uniform(-6.5, -3.5)
    
    return {
        "title": title,
        "content": content.strip(),
        "sentiment_context": "analyst_upgrade" if positive else "analyst_downgrade",
        "expected_score": sentiment_hint
    }


def generate_random_article(company: Dict) -> Dict:
    """Generate a random article type with random sentiment."""
    generators = [
        generate_earnings_beat_article,
        generate_product_announcement,
        generate_partnership_article,
        generate_regulatory_article,
        generate_leadership_article,
        generate_market_analysis_article
    ]
    
    generator = random.choice(generators)
    positive = random.choice([True, True, True, False, False])  # 60% positive, 40% negative
    
    return generator(company, positive)


def create_article_files(company: Dict, num_articles: int, base_dir: Path) -> List[Tuple[Path, Dict, float]]:
    """Create article files for a company."""
    articles = []
    articles_dir = base_dir / "demo_real_world" / company["symbol"]
    articles_dir.mkdir(parents=True, exist_ok=True)
    
    now = datetime.datetime.now(datetime.timezone.utc)
    
    for i in range(num_articles):
        article_data = generate_random_article(company)
        
        # Create full article object
        article = {
            "source": "demo_real_world",
            "topic": company["symbol"],
            "title": article_data["title"],
            "url": f"https://example.com/{company['symbol'].lower()}/article{i+1}",
            "published_at": (now - datetime.timedelta(
                days=random.randint(0, 14),
                hours=random.randint(0, 23)
            )).isoformat(),
            "content": article_data["content"],
            "author": random.choice([
                "Financial News Desk", "Market Reporter", "Industry Analyst",
                "Business Editor", "Senior Correspondent", "Technology Reporter",
                "Investment News Team", "Economics Writer"
            ]),
            "sentiment_context": article_data["sentiment_context"]
        }
        
        filename = f"{i+1:03d}_{company['symbol'].lower()}_article.json"
        filepath = articles_dir / filename
        
        with open(filepath, "w") as f:
            json.dump(article, f, indent=2)
        
        articles.append((filepath, article, article_data.get("expected_score", 0.0)))
    
    return articles


def mock_score_articles(articles: List[Tuple[Path, Dict, float]], base_dir: Path) -> Dict:
    """Score articles using mock scores."""
    llm_scores_dir = base_dir / "llm_scores"
    results = {}
    
    for article_file, article, expected_score in articles:
        topic = article["topic"]
        
        # Add some random variance to expected score
        score = expected_score + random.uniform(-0.5, 0.5)
        score = max(-10.0, min(10.0, score))  # Clamp to valid range
        
        # Generate explanation based on score
        if score >= 7.0:
            explanation_base = "Exceptional positive news with major strategic implications"
        elif score >= 4.0:
            explanation_base = "Strong positive developments and favorable outlook"
        elif score >= 2.0:
            explanation_base = "Moderate positive news with some encouraging signs"
        elif score >= 0.5:
            explanation_base = "Slightly positive with minor favorable elements"
        elif score > -0.5:
            explanation_base = "Neutral reporting with balanced perspective"
        elif score > -2.0:
            explanation_base = "Slightly negative with minor concerns"
        elif score > -4.0:
            explanation_base = "Moderate negative news with notable issues"
        elif score > -7.0:
            explanation_base = "Significant negative developments raising concerns"
        else:
            explanation_base = "Severe negative news with major implications"
        
        explanation = f"{explanation_base}. {article['sentiment_context'].replace('_', ' ').title()}."
        
        # Save score
        save_llm_score(article_file, article, score, explanation, llm_scores_dir, "mock-model")
        
        if topic not in results:
            results[topic] = []
        results[topic].append({
            "title": article["title"],
            "score": score,
            "explanation": explanation
        })
    
    return results


def real_score_articles(articles: List[Tuple[Path, Dict, float]], 
                       prompt_template: str, api_key: str, 
                       base_dir: Path, model: str = "gpt-4o-mini") -> Dict:
    """Score articles using OpenAI API."""
    llm_scores_dir = base_dir / "llm_scores"
    results = {}
    
    print("\nAnalyzing articles with OpenAI API...")
    print(f"Model: {model}")
    print(f"Total articles: {len(articles)}\n")
    
    for i, (article_file, article, _) in enumerate(articles, 1):
        topic = article["topic"]
        print(f"[{i}/{len(articles)}] {topic}: {article['title'][:50]}... ", end="", flush=True)
        
        # Format prompt
        full_prompt = format_prompt(prompt_template, article, "")
        
        # Call OpenAI API
        response_text = call_openai_api(full_prompt, api_key, model)
        
        if response_text is None:
            print("✗ Failed")
            continue
        
        # Parse response
        score, explanation = parse_llm_response(response_text)
        
        if score is not None:
            print(f"✓ Score: {score:+.2f}")
            
            # Save score
            save_llm_score(article_file, article, score, explanation, llm_scores_dir, model)
            
            if topic not in results:
                results[topic] = []
            results[topic].append({
                "title": article["title"],
                "score": score,
                "explanation": explanation
            })
        else:
            print("✗ Parse failed")
    
    return results


def generate_recommendations(base_dir: Path):
    """Generate investment recommendations from scores."""
    print("\n" + "=" * 80)
    print("GENERATING RECOMMENDATIONS")
    print("=" * 80)
    
    try:
        from scoring.recommendation_engine import process_topic_recommendation
    except ImportError:
        print("⚠ Recommendation engine not available, skipping...")
        return
    
    llm_scores_dir = base_dir / "llm_scores"
    recommendations_dir = base_dir / "recommendations"
    recommendations_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all topics with scores
    topics = [d.name for d in llm_scores_dir.iterdir() if d.is_dir()]
    
    print(f"\nProcessing {len(topics)} topics...")
    
    for topic in sorted(topics):
        topic_scores_dir = llm_scores_dir / topic
        score_files = list(topic_scores_dir.glob("*_score.json"))
        
        if not score_files:
            print(f"  ✗ {topic}: No score files found")
            continue
        
        print(f"  Processing {topic}: {len(score_files)} articles... ", end="", flush=True)
        
        result = process_topic_recommendation(topic, score_files, recommendations_dir)
        
        if result:
            rec = result['recommendation']['recommendation']
            score = result['aggregation']['score']
            print(f"✓ {rec} (score: {score:+.2f})")
        else:
            print("✗ Failed")


def create_demo_config(base_dir: Path):
    """Create configuration file for the demo."""
    config = {
        "topics": [company["symbol"] for company in COMPANIES],
        "sources": ["demo_real_world"],
        "max_age_days": 14,
        "fetch_full_content": True,
        "fetch_full_top_n": 10,
        "content_extractor": "readability",
        "max_content_chars": 6000
    }
    
    config_file = base_dir / "demo_real_world_config.json"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✓ Created configuration file: {config_file}")
    return config_file


def show_summary(scoring_results: Dict):
    """Display summary of results."""
    print("\n" + "=" * 80)
    print("SUMMARY OF RESULTS")
    print("=" * 80)
    
    print(f"\n{'Topic':<8} {'Articles':<10} {'Avg Score':<12} {'Sentiment'}")
    print("-" * 80)
    
    all_scores = []
    for topic in sorted(scoring_results.keys()):
        articles = scoring_results[topic]
        avg_score = sum(a["score"] for a in articles) / len(articles)
        all_scores.append(avg_score)
        
        if avg_score >= 4.0:
            sentiment = "Very Positive ↑↑"
        elif avg_score >= 2.0:
            sentiment = "Positive ↑"
        elif avg_score >= 0.5:
            sentiment = "Slightly Positive"
        elif avg_score > -0.5:
            sentiment = "Neutral →"
        elif avg_score > -2.0:
            sentiment = "Slightly Negative"
        elif avg_score > -4.0:
            sentiment = "Negative ↓"
        else:
            sentiment = "Very Negative ↓↓"
        
        print(f"{topic:<8} {len(articles):<10} {avg_score:+6.2f}      {sentiment}")
    
    print("-" * 80)
    overall_avg = sum(all_scores) / len(all_scores) if all_scores else 0
    print(f"{'OVERALL':<8} {sum(len(a) for a in scoring_results.values()):<10} {overall_avg:+6.2f}")


def main():
    """Run the real world demo."""
    print("\n" + "=" * 80)
    print("VUTS - REAL WORLD DEMONSTRATION")
    print("=" * 80)
    print("\nThis demo showcases the VUTS system at scale with:")
    print(f"  • {len(COMPANIES)} companies across multiple sectors")
    print("  • 15-23 articles per company (variable)")
    print("  • Diverse writing styles and sentiments")
    print("  • Realistic scenarios (for demonstration purposes)\n")
    
    # Check for OpenAI API key
    api_key = os.environ.get("OPENAI_API_KEY")
    use_openai = api_key and OPENAI_AVAILABLE
    
    if use_openai:
        print("✓ OpenAI API key detected - will use real sentiment analysis")
        estimated_articles = len(COMPANIES) * 17  # Average
        estimated_cost = estimated_articles * 0.0006
        print(f"  Estimated articles: ~{estimated_articles}")
        print(f"  Estimated cost: ~${estimated_cost:.2f}")
        print("\n⚠  Note: This will make real API calls. Press Ctrl+C to cancel.")
        print("  Or unset OPENAI_API_KEY to use mock scoring.")
        try:
            input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            return 0
    else:
        print("ℹ No OpenAI API key - using mock sentiment scoring")
        print("  Set OPENAI_API_KEY environment variable for real analysis")
    
    # Setup
    demo_dir = Path(__file__).parent.parent / "demo_output_real_world"
    demo_dir.mkdir(exist_ok=True)
    
    # Load prompt template if using OpenAI
    prompt_template = None
    if use_openai:
        prompt_file = Path(__file__).parent.parent / "src" / "llm" / "sentiment_prompt.txt"
        from llm.sentiment_analyzer import load_prompt_template
        prompt_template = load_prompt_template(prompt_file)
    
    # Create articles
    print("\n" + "=" * 80)
    print("GENERATING ARTICLES")
    print("=" * 80)
    
    all_articles = []
    for company in COMPANIES:
        num_articles = random.randint(15, 23)  # Variable: 15-23 articles per company
        print(f"\n{company['symbol']}: Generating {num_articles} articles for {company['name']}")
        articles = create_article_files(company, num_articles, demo_dir)
        all_articles.extend(articles)
        print(f"  ✓ Created {len(articles)} articles")
    
    print(f"\n✓ Total articles generated: {len(all_articles)}")
    
    # Score articles
    print("\n" + "=" * 80)
    print("SCORING ARTICLES")
    print("=" * 80)
    
    if use_openai:
        scoring_results = real_score_articles(all_articles, prompt_template, api_key, demo_dir)
    else:
        print("\nUsing mock scoring (set OPENAI_API_KEY for real analysis)...")
        scoring_results = mock_score_articles(all_articles, demo_dir)
        print(f"✓ Scored {len(all_articles)} articles")
    
    # Show summary
    show_summary(scoring_results)
    
    # Generate recommendations
    generate_recommendations(demo_dir)
    
    # Create config file
    config_file = create_demo_config(demo_dir)
    
    # Final summary
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print(f"\n📁 Output directory: {demo_dir}")
    print(f"   • Articles: {demo_dir / 'demo_real_world'}")
    print(f"   • Scores: {demo_dir / 'llm_scores'}")
    print(f"   • Recommendations: {demo_dir / 'recommendations'}")
    print(f"   • Config: {config_file}")
    
    print("\n📊 Quick Stats:")
    print(f"   • Companies: {len(COMPANIES)}")
    print(f"   • Total articles: {len(all_articles)}")
    print(f"   • Topics analyzed: {len(scoring_results)}")
    
    print("\n🚀 Next Steps:")
    print("   1. Review the generated articles and scores")
    print("   2. View recommendations in the recommendations directory")
    print("   3. Launch the web UI to visualize results:")
    print("      cd .. && ./vuts ui")
    print("   4. Point the UI to the demo data directory")
    
    print("\n⚠️  Disclaimer:")
    print("   This is a demonstration with simulated scenarios.")
    print("   Not financial advice. For educational purposes only.")
    
    return 0


if __name__ == "__main__":
    exit(main())
