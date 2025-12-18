"""System constants for MoIE-OS Protocol."""

# VDR Thresholds
MIN_VDR = 0.1  # Below this = candidate for deletion
HEALTHY_VDR = 0.5  # Above this = healthy component
EXCELLENT_VDR = 1.0  # Above this = excellent component

# Alignment Thresholds
MIN_RESONANCE = 0.5  # Below this = veto by Lord Wilson
HEALTHY_RESONANCE = 0.7  # Above this = good alignment

# Ouroboros Settings
PURGATORY_TTL_DAYS = 30  # Days before permanent deletion
SCAN_INTERVAL_HOURS = 24  # How often to scan for low-VDR components

# Expert Settings
EXPERT_TTL_SECONDS = 300  # 5 minutes - experts are ephemeral
MAX_EXPERTS_PER_TASK = 3  # Top-k routing

# Kill Chain Settings
MAX_STAGE_RETRIES = 2
STAGE_TIMEOUT_SECONDS = 60

# Complexity Metrics
ALPHA_DEFAULT = 1.5  # Complexity penalty exponent
MAX_COMPLEXITY_SCORE = 10.0  # Maximum density score

# CIRL Settings
MAX_CIRL_ITERATIONS = 100  # Maximum feedback loops
CIRL_LEARNING_RATE = 0.1  # How fast to update from feedback
