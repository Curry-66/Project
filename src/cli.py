import click
from rich.console import Console

console = Console()

@click.group()
def main():
    """AI 智能体开发学习项目命令行工具"""
    pass

@main.command()
def hello():
    """向智能体打招呼"""
    console.print("[bold green]Hello, AI Agent![/bold green]")
    console.print("欢迎使用 AI 智能体开发学习项目")

@main.command()
def version():
    """显示项目版本"""
    from . import __version__
    console.print(f"[bold blue]AI Agent Learning Project v{__version__}[/bold blue]")

if __name__ == '__main__':
    main()
