"""
Seed script: Creates demo tenant, user, 20 companies, synthetic ESG events and scores.
Run: python -m scripts.seed
"""
import asyncio
import random
import uuid
from datetime import datetime, timedelta, timezone

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import text
from app.db.session import async_session, engine, Base
from app.db.models import (
    Tenant, User, Company, ESGEvent, ESGScore, RAGDocument,
    Watchlist, WatchlistItem, AlertRule,
)
from app.core.auth import hash_password
from app.services.rag import upsert_document

DEMO_TENANT_ID = "00000000-0000-0000-0000-000000000001"
DEMO_USER_ID = "00000000-0000-0000-0000-000000000002"

COMPANIES = [
    ("Tata Steel Ltd", "TATASTEEL", "Materials", "India"),
    ("Reliance Industries", "RELIANCE", "Energy", "India"),
    ("Infosys Ltd", "INFY", "Technology", "India"),
    ("Adani Green Energy", "ADANIGREEN", "Utilities", "India"),
    ("HDFC Bank", "HDFCBANK", "Financials", "India"),
    ("ITC Limited", "ITC", "Consumer Staples", "India"),
    ("Mahindra & Mahindra", "M&M", "Industrials", "India"),
    ("Wipro Ltd", "WIPRO", "Technology", "India"),
    ("Bharti Airtel", "BHARTIARTL", "Telecom", "India"),
    ("Larsen & Toubro", "LT", "Industrials", "India"),
    ("JSW Steel", "JSWSTEEL", "Materials", "India"),
    ("NTPC Limited", "NTPC", "Utilities", "India"),
    ("Sun Pharma", "SUNPHARMA", "Healthcare", "India"),
    ("Coal India", "COALINDIA", "Energy", "India"),
    ("Hindustan Unilever", "HINDUNILVR", "Consumer Staples", "India"),
    ("Asian Paints", "ASIANPAINT", "Materials", "India"),
    ("Bajaj Finance", "BAJFINANCE", "Financials", "India"),
    ("Power Grid Corp", "POWERGRID", "Utilities", "India"),
    ("UltraTech Cement", "ULTRACEMCO", "Materials", "India"),
    ("Vedanta Ltd", "VEDL", "Materials", "India"),
]

EVENT_TEMPLATES = {
    "environmental": [
        ("Carbon emission targets missed by {pct}%", "The company failed to meet its annual carbon reduction targets, exceeding planned emissions by {pct}%. This raises concerns about the company's commitment to climate goals and may affect ESG ratings."),
        ("New renewable energy plant commissioned", "The company has commissioned a {mw}MW solar/wind energy facility, demonstrating commitment to clean energy transition and reducing carbon footprint."),
        ("Water pollution incident at {location} plant", "Regulatory authorities detected elevated levels of pollutants in water discharge from the company's {location} manufacturing facility. Investigation is ongoing."),
        ("Deforestation linked to supply chain", "An environmental NGO report links the company's raw material sourcing to deforestation in {location}. The company has not yet responded to the allegations."),
        ("Achieved zero-waste certification", "The company's {location} facility has achieved zero-waste-to-landfill certification, a significant milestone in its sustainability journey."),
        ("Plastic packaging reduction initiative", "The company announced a plan to reduce single-use plastic packaging by {pct}% over the next 3 years across all product lines."),
    ],
    "social": [
        ("Worker safety incident at {location}", "A workplace accident at the {location} facility resulted in injuries to {num} workers. The company has initiated an internal investigation and temporarily halted operations."),
        ("Gender diversity improvement in leadership", "The company increased female representation in senior leadership to {pct}%, up from the previous year, aligning with its diversity commitments."),
        ("Labor rights violation allegations", "A labor union has filed complaints alleging unfair working conditions and wage disputes at the company's {location} operations."),
        ("Community development program launched", "The company launched a ₹{amount} crore community development program focusing on education and healthcare in {location}."),
        ("Data privacy breach affecting {num} users", "A cybersecurity incident exposed personal data of approximately {num} customers. The company has notified affected individuals and regulatory authorities."),
        ("Employee wellness program expanded", "The company expanded its mental health and wellness support program to cover all {num} employees globally."),
    ],
    "governance": [
        ("Board independence concerns raised", "Proxy advisory firm flagged that only {pct}% of board members are independent, below the recommended threshold for good governance."),
        ("Executive compensation controversy", "Shareholders have raised concerns about the CEO's ₹{amount} crore compensation package, which is {pct}% above industry median."),
        ("Anti-corruption policy strengthened", "The company adopted enhanced anti-corruption and whistleblower protection policies following recommendations from an independent audit."),
        ("Related party transaction scrutiny", "SEBI is examining related party transactions worth ₹{amount} crore between the company and entities linked to promoter family members."),
        ("ESG committee established at board level", "The board has constituted a dedicated ESG committee to oversee sustainability strategy, reporting, and compliance."),
        ("Audit qualification on financial statements", "The statutory auditor issued a qualified opinion on the annual financial statements, citing concerns about inventory valuation methods."),
    ],
}


def gen_event(category: str, company_name: str) -> tuple:
    templates = EVENT_TEMPLATES[category]
    title_tpl, desc_tpl = random.choice(templates)
    locations = ["Mumbai", "Chennai", "Delhi", "Bangalore", "Kolkata", "Hyderabad", "Pune", "Jaipur"]
    replacements = {
        "pct": str(random.randint(5, 45)),
        "mw": str(random.randint(50, 500)),
        "location": random.choice(locations),
        "num": str(random.randint(3, 50000)),
        "amount": str(random.randint(10, 5000)),
    }
    title = title_tpl.format(**replacements)
    desc = desc_tpl.format(**replacements)
    return title, desc


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        existing = await db.execute(text(f"SELECT id FROM tenants WHERE id = '{DEMO_TENANT_ID}'"))
        if existing.scalar_one_or_none():
            print("Demo data already exists. Skipping seed.")
            return

        tenant = Tenant(id=DEMO_TENANT_ID, name="Green Bharat Demo", slug="green-bharat-demo")
        db.add(tenant)

        user = User(
            id=DEMO_USER_ID,
            tenant_id=DEMO_TENANT_ID,
            email="demo@greenbharat.ai",
            password_hash=hash_password("demo123"),
            full_name="Demo User",
            role="admin",
        )
        db.add(user)
        await db.flush()

        company_ids = []
        for name, ticker, sector, country in COMPANIES:
            cid = str(uuid.uuid4())
            company_ids.append(cid)
            company = Company(
                id=cid,
                tenant_id=DEMO_TENANT_ID,
                name=name,
                ticker=ticker,
                sector=sector,
                country=country,
                description=f"{name} is a leading {sector.lower()} company based in {country}.",
            )
            db.add(company)

        await db.flush()
        now = datetime.now(timezone.utc)

        for cid in company_ids:
            num_events = random.randint(8, 20)
            for i in range(num_events):
                category = random.choice(["environmental", "social", "governance"])
                title, desc = gen_event(category, "")
                severity = random.randint(2, 9)
                confidence = round(random.uniform(0.5, 0.95), 2)
                sentiment = "negative" if severity > 5 else random.choice(["positive", "neutral", "negative"])
                event_date = now - timedelta(days=random.randint(0, 60), hours=random.randint(0, 23))

                event = ESGEvent(
                    tenant_id=DEMO_TENANT_ID,
                    company_id=cid,
                    title=title,
                    description=desc,
                    category=category,
                    subcategory="general",
                    severity=severity,
                    confidence=confidence,
                    sentiment=sentiment,
                    event_date=event_date,
                    raw_text=f"{title}. {desc}",
                    is_processed=True,
                    classification_json={
                        "category": category,
                        "subcategory": "general",
                        "severity": severity,
                        "confidence": confidence,
                        "sentiment": sentiment,
                    },
                )
                db.add(event)
                await db.flush()

                rag_doc = RAGDocument(
                    tenant_id=DEMO_TENANT_ID,
                    company_id=cid,
                    event_id=event.id,
                    title=title,
                    content=f"{title}. {desc}",
                    source_url=f"https://news.example.com/esg/{event.id[:8]}",
                )
                db.add(rag_doc)
                await db.flush()

                await upsert_document(
                    doc_id=rag_doc.id,
                    text=rag_doc.content,
                    metadata={
                        "tenant_id": DEMO_TENANT_ID,
                        "company_id": cid,
                        "title": title,
                        "source_url": rag_doc.source_url,
                        "ts": event_date.isoformat(),
                        "text": rag_doc.content[:500],
                    },
                )

            for day_offset in range(30, -1, -1):
                base = 75 - random.uniform(0, 25)
                e_score = max(10, base + random.uniform(-10, 10))
                s_score = max(10, base + random.uniform(-10, 10))
                g_score = max(10, base + random.uniform(-10, 10))
                overall = e_score * 0.35 + s_score * 0.30 + g_score * 0.35

                risk = "low" if overall >= 80 else "medium" if overall >= 60 else "high" if overall >= 40 else "critical"

                score = ESGScore(
                    tenant_id=DEMO_TENANT_ID,
                    company_id=cid,
                    overall=round(overall, 2),
                    environmental=round(e_score, 2),
                    social=round(s_score, 2),
                    governance=round(g_score, 2),
                    risk_level=risk,
                    recorded_at=now - timedelta(days=day_offset),
                )
                db.add(score)

        watchlist = Watchlist(
            tenant_id=DEMO_TENANT_ID,
            user_id=DEMO_USER_ID,
            name="My ESG Watchlist",
        )
        db.add(watchlist)
        await db.flush()

        for cid in company_ids[:5]:
            item = WatchlistItem(watchlist_id=watchlist.id, company_id=cid)
            db.add(item)

        alert_rule = AlertRule(
            tenant_id=DEMO_TENANT_ID,
            user_id=DEMO_USER_ID,
            name="High Severity Alert",
            condition_type="severity_gte",
            threshold=7,
            channels=["email", "slack"],
        )
        db.add(alert_rule)

        await db.commit()
        print(f"Seeded: 1 tenant, 1 user, {len(company_ids)} companies, events, scores, watchlist, alert rule")
        print(f"Login: demo@greenbharat.ai / demo123")


if __name__ == "__main__":
    asyncio.run(seed())
