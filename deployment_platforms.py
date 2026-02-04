"""
DeepAgent Platform Intelligence Library
Tier 1: Essential deployment platforms, IaC, and security baselines.
"""

PLATFORMS = {
    'vercel': {
        'name': 'Vercel',
        'config_file': 'vercel.json',
        'use_cases': ['Next.js', 'React', 'Vue', 'Static Sites', 'Serverless'],
        'cost_profile': '$0/mo (Hobby) to $20/mo (Pro)',
        'setup_complexity': 'Low (1 agent-hour)',
        'template': {
            "version": 2,
            "builds": [{"src": "package.json", "use": "@vercel/next"}],
            "env": {"DATABASE_URL": "@database_url"}
        }
    },
    'render': {
        'name': 'Render',
        'config_file': 'render.yaml',
        'use_cases': ['Web Services', 'Background Workers', 'Managed PostgreSQL/Redis'],
        'cost_profile': '$0/mo (Free tier) to $7+/mo (Starter)',
        'setup_complexity': 'Low-Medium (2 agent-hours)',
        'template': {
            "services": [
                {
                    "type": "web",
                    "name": "api",
                    "env": "python",
                    "buildCommand": "pip install -r requirements.txt",
                    "startCommand": "gunicorn app:app"
                }
            ]
        }
    },
    'railway': {
        'name': 'Railway',
        'config_file': 'railway.json',
        'use_cases': ['Full-stack Apps', 'Cron Jobs', 'Databases', 'Dockerized Services'],
        'cost_profile': '$5-15/mo (Standard usage)',
        'setup_complexity': 'Low (1 agent-hour)',
        'template': {
            "version": 2,
            "build": {"builder": "DOCKER"},
            "deploy": {"numReplicas": 1}
        }
    },
    'terraform': {
        'name': 'Terraform (Infrastructure as Code)',
        'config_file': 'main.tf',
        'use_cases': ['AWS/GCP/Azure Provisioning', 'Multi-cloud Management', 'Enterprise Compliance'],
        'cost_profile': 'Variable (Cloud provider dependent)',
        'setup_complexity': 'High (4-8 agent-hours)',
        'template': {
            "provider": "aws",
            "resource": "aws_instance",
            "variables": "variables.tf",
            "state": "remote_s3_backend"
        }
    },
    'security_baseline': {
        'name': '.env Security Pattern',
        'config_file': '.env.example',
        'use_cases': ['Secrets Management', 'Environment Parity'],
        'template': {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/db",
            "API_KEY": "your_api_key_here",
            "NODE_ENV": "production"
        }
    }
}
