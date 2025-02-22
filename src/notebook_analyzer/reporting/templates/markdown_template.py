from typing import Dict, Any, List
import json
import base64
import io
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

class MarkdownTemplate:
    """
    Markdown template generator for notebook analysis reports.
    
    This class handles the creation and rendering of Markdown reports
    with embedded images for charts and structured sections.
    """

    def __init__(self, output_dir: str = "reports"):
        """
        Initialize the Markdown template generator.

        Args:
            output_dir (str): Directory for storing generated images
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.chart_generators = self._get_chart_generators()

    def render(self, report_data: Dict[str, Any]) -> str:
        """
        Render the report data into Markdown format.

        Args:
            report_data (Dict[str, Any]): The report data to render

        Returns:
            str: Rendered Markdown content
        """
        sections = []
        
        # Add header
        sections.append(self._render_header(report_data))
        
        # Add table of contents
        sections.append(self._render_toc(report_data))
        
        # Add sections
        sections.append("---\n")  # Add separator after TOC
        for section in report_data['sections']:
            sections.append(self._render_section(section))
            sections.append("\n---\n")  # Add separator between sections
        
        # Add footer
        sections.append(self._render_footer(report_data))
        
        return '\n'.join(sections)

    def _render_header(self, report_data: Dict[str, Any]) -> str:
        """Render the report header."""
        return (
            f"# {report_data['title']}\n\n"
            f"> Generated: {report_data['timestamp']}  \n"
            f"> Overall Score: {report_data.get('overall_score', 0):.2f}/100\n\n"
            "---"
        )

    def _render_toc(self, report_data: Dict[str, Any]) -> str:
        """Render the table of contents."""
        sections = ["## Table of Contents\n"]
        
        # Add each section to TOC with proper link formatting
        for i, section in enumerate(report_data['sections'], 1):
            link = section['title'].lower().replace(' ', '-')
            sections.append(f"{i}. [{section['title']}](#{link})")
        
        return '\n'.join(sections)

    def _render_section(self, section: Dict[str, Any]) -> str:
        """
        Render a report section.
        
        Args:
            section (Dict[str, Any]): Section data including title, content, findings, etc.
            
        Returns:
            str: Formatted section content
        """
        parts = []
        
        # Add section title
        parts.append(f"## {section['title']}\n")
        
        # Add score if present
        if 'score' in section:
            parts.append(f"> Section Score: {section['score']:.2f}/100\n")
        
        # Add content
        if section.get('content'):
            # If content is a list, join with newlines
            if isinstance(section['content'], list):
                parts.append('\n'.join(section['content']))
            else:
                parts.append(str(section['content']))
            parts.append('\n')
        
        # Add charts if present
        if section.get('charts'):
            chart_content = self._render_charts(section['charts'])
            if chart_content:
                parts.append("\n### Charts\n")
                parts.append(chart_content)
                parts.append('\n')
        
        # Add findings
        if section.get('findings'):
            parts.append("\n### Key Findings\n")
            for finding in section['findings']:
                parts.append(f"- {finding}")
            parts.append('\n')
        
        # Add suggestions
        if section.get('suggestions'):
            parts.append("\n### Suggestions\n")
            for suggestion in section['suggestions']:
                parts.append(f"- {suggestion}")
            parts.append('\n')
        
        return '\n'.join(parts)

    def _render_footer(self, report_data: Dict[str, Any]) -> str:
        """Render the report footer."""
        year = datetime.now().year
        return (
            f"\nGenerated by Notebook Analyzer v{report_data.get('version', '1.0.0')}  \n"
            f"© {year} Notebook Analyzer"
        )

    def _render_charts(self, charts: List[Dict[str, Any]]) -> str:
        """Render charts as embedded images."""
        if not charts:
            return ""
            
        chart_md = []
        for chart in charts:
            try:
                image_path = self._generate_chart_image(chart)
                title = chart.get('title', 'Chart')
                chart_md.append(f"![{title}]({image_path})")
            except Exception as e:
                print(f"Failed to generate chart: {str(e)}")
                continue
        
        return '\n'.join(chart_md)

    def _get_chart_generators(self) -> Dict[str, callable]:
        """
        Get the chart generation functions.

        Returns:
            Dict[str, callable]: Chart type to generator mapping
        """
        return {
            'bar': self._generate_bar_chart,
            'line': self._generate_line_chart,
            'pie': self._generate_pie_chart,
            'radar': self._generate_radar_chart,
            'heatmap': self._generate_heatmap,
            'histogram': self._generate_histogram,
            'network': self._generate_network_graph
        }

    def _generate_chart_image(self, chart_data: Dict[str, Any]) -> str:
        """
        Generate a chart image and save it.

        Args:
            chart_data (Dict[str, Any]): Chart data

        Returns:
            str: Path to the generated image
        """
        plt.figure(figsize=(10, 6))
        
        # Generate the chart using the appropriate generator
        if chart_data['type'] in self.chart_generators:
            self.chart_generators[chart_data['type']](chart_data)
        
        # Add title if present
        if 'title' in chart_data:
            plt.title(chart_data['title'])
        
        # Save the chart
        image_path = f"{self.output_dir}/chart_{chart_data['id']}.png"
        plt.savefig(image_path, bbox_inches='tight', dpi=300)
        plt.close()
        
        return image_path

    def _generate_bar_chart(self, chart_data: Dict[str, Any]) -> None:
        """Generate a bar chart."""
        sns.barplot(x=list(chart_data['data'].keys()),
                   y=list(chart_data['data'].values()))
        plt.xticks(rotation=45)

    def _generate_line_chart(self, chart_data: Dict[str, Any]) -> None:
        """Generate a line chart."""
        plt.plot(chart_data['x'], chart_data['y'], marker='o')

    def _generate_pie_chart(self, chart_data: Dict[str, Any]) -> None:
        """Generate a pie chart."""
        plt.pie(list(chart_data['data'].values()),
                labels=list(chart_data['data'].keys()),
                autopct='%1.1f%%')

    def _generate_radar_chart(self, chart_data: Dict[str, Any]) -> None:
        """Generate a radar chart."""
        categories = list(chart_data['data'].keys())
        values = list(chart_data['data'].values())
        
        angles = [n / float(len(categories)) * 2 * 3.14159 for n in range(len(categories))]
        values += values[:1]
        angles += angles[:1]
        
        ax = plt.subplot(111, projection='polar')
        ax.plot(angles, values)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)

    def _generate_heatmap(self, chart_data: Dict[str, Any]) -> None:
        """Generate a heatmap."""
        sns.heatmap(chart_data['data'], annot=True, cmap='YlOrRd')

    def _generate_histogram(self, chart_data: Dict[str, Any]) -> None:
        """Generate a histogram."""
        plt.hist(chart_data['data'], bins='auto')

    def _generate_network_graph(self, chart_data: Dict[str, Any]) -> None:
        """Generate a network graph."""
        # Use networkx for network visualization
        import networkx as nx
        G = nx.Graph()
        
        # Add nodes and edges
        for node in chart_data['nodes']:
            G.add_node(node['id'])
        for edge in chart_data['edges']:
            G.add_edge(edge['source'], edge['target'])
        
        nx.draw(G, with_labels=True, node_color='lightblue',
                node_size=500, font_size=10)
