import os
import datetime as dt
from typing import List, Dict, Optional

import requests
import numpy as np

# ====== Opcjonalny import transformers ======
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class MarketSentimentAnalyzer:
    """
    Moduł do pobierania newsów z internetu i liczenia sentymentu
    dla danego tickera / rynku.
    """

    def __init__(
        self,
        news_api_key: Optional[str] = None,
        days_back: int = 2,
        language: str = "en",
    ):
        """
        :param news_api_key: klucz do NewsAPI (https://newsapi.org)
                             jeśli None -> czyta z ENV: NEWSAPI_KEY
        :param days_back: ile dni wstecz pobierać newsy
        :param language: język newsów (np. 'en', 'pl')
        """
        self.news_api_key = news_api_key or os.getenv("NEWSAPI_KEY", "")
        self.days_back = days_back
        self.language = language

        if TRANSFORMERS_AVAILABLE:
            # Domyślny model ogólnego sentymentu
            self.sentiment_pipeline = pipeline("sentiment-analysis")
        else:
            self.sentiment_pipeline = None

    # ========= NEWSAPI =========
    def _fetch_news_from_newsapi(self, query: str) -> List[Dict]:
        """
        Pobiera newsy z NewsAPI dla danego zapytania (np. 'AAPL').
        Zwraca listę artykułów (dict z 'title' i 'description').
        """
        if not self.news_api_key:
            raise RuntimeError(
                "Brak klucza NEWSAPI_KEY. Ustaw zmienną środowiskową lub "
                "przekaż news_api_key do MarketSentimentAnalyzer."
            )

        end = dt.datetime.utcnow()
        start = end - dt.timedelta(days=self.days_back)

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "from": start.strftime("%Y-%m-%d"),
            "to": end.strftime("%Y-%m-%d"),
            "sortBy": "publishedAt",
            "language": self.language,
            "pageSize": 50,
            "apiKey": self.news_api_key,
        }

        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        articles = data.get("articles", [])
        cleaned = []
        for a in articles:
            title = a.get("title") or ""
            desc = a.get("description") or ""
            if title or desc:
                cleaned.append(
                    {
                        "title": title.strip(),
                        "description": desc.strip(),
                    }
                )
        return cleaned

    # ========= SENTIMENT ANALIZA =========
    def _analyze_texts_transformers(self, texts: List[str]) -> List[float]:
        """
        Analiza sentymentu z użyciem transformers.
        Zwraca listę wyników w skali [-1, 1].
        """
        results = self.sentiment_pipeline(texts, truncation=True)
        scores = []
        for r in results:
            label = r["label"].upper()
            score = float(r["score"])
            # Przekształcenie na [-1, 1]
            if "NEG" in label:
                scores.append(-score)
            else:
                scores.append(score)
        return scores

    def _analyze_texts_fallback(self, texts: List[str]) -> List[float]:
        """
        Prosty fallback bez transformers – leksykalny licznik słów.
        Bardzo uproszczone, ale działa bez zewnętrznych modeli.
        """
        positive_words = ["good", "great", "bullish", "gain", "profit", "upgrade", "beat"]
        negative_words = ["bad", "worse", "bearish", "loss", "downgrade", "miss"]

        scores = []
        for t in texts:
            txt = t.lower()
            pos = sum(w in txt for w in positive_words)
            neg = sum(w in txt for w in negative_words)
            if pos + neg == 0:
                scores.append(0.0)
            else:
                score = (pos - neg) / float(pos + neg)
                scores.append(score)
        return scores

    def analyze_news_for_ticker(self, ticker: str) -> Dict:
        """
        Główna funkcja:
        1) pobiera newsy dla tickera,
        2) liczy sentyment dla każdego,
        3) zwraca agregaty.
        """
        query = ticker.upper()
        articles = self._fetch_news_from_newsapi(query)

        if not articles:
            return {
                "ticker": ticker.upper(),
                "num_articles": 0,
                "avg_sentiment": 0.0,
                "positive_ratio": 0.0,
                "negative_ratio": 0.0,
                "neutral_ratio": 0.0,
                "details": [],
            }

        texts = [
            (a["title"] + " " + a["description"]).strip()
            for a in articles
            if (a.get("title") or a.get("description"))
        ]

        if not texts:
            return {
                "ticker": ticker.upper(),
                "num_articles": 0,
                "avg_sentiment": 0.0,
                "positive_ratio": 0.0,
                "negative_ratio": 0.0,
                "neutral_ratio": 1.0,
                "details": [],
            }

        # Wybór silnika sentimentu
        if self.sentiment_pipeline is not None:
            scores = self._analyze_texts_transformers(texts)
        else:
            scores = self._analyze_texts_fallback(texts)

        scores_arr = np.array(scores)
        avg_sent = float(scores_arr.mean())

        pos_mask = scores_arr > 0.1
        neg_mask = scores_arr < -0.1
        neu_mask = ~ (pos_mask | neg_mask)

        n = len(scores_arr)
        positive_ratio = float(pos_mask.sum()) / n
        negative_ratio = float(neg_mask.sum()) / n
        neutral_ratio = float(neu_mask.sum()) / n

        details = []
        for art, s in zip(articles, scores):
            details.append(
                {
                    "title": art["title"],
                    "description": art["description"],
                    "score": float(s),
                }
            )

        return {
            "ticker": ticker.upper(),
            "num_articles": n,
            "avg_sentiment": avg_sent,
            "positive_ratio": positive_ratio,
            "negative_ratio": negative_ratio,
            "neutral_ratio": neutral_ratio,
            "details": details,
        }
