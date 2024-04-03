ATTACH ':memory:' AS my_domain;
ATTACH ':memory:' AS your_domain;

CREATE SCHEMA IF NOT EXISTS my_domain.alpha;
CREATE SCHEMA IF NOT EXISTS my_domain.beta;