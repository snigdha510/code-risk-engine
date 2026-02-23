def compute_risk_score(impact_size, depth, centrality, reverse_impact):
    score = 0.0
    
    score += min(impact_size / 50, 1.0) * 0.4
    score += min(depth / 10, 1.0) * 0.2
    score += min(reverse_impact / 50, 1.0) * 0.3
    score += min(centrality * 5, 1.0) * 0.1

    return round(min(score, 1.0), 3)