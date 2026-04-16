from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

setup(
    name='ai-agent-learning',
    version='0.1.0',
    description='AI 智能体开发学习项目',
    long_description=open('README.md').read() if open('README.md', 'r').read() else 'AI 智能体开发学习项目',
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/ai-agent-learning',
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'ai-agent=src.cli:main',
        ],
    },
)
