import { Component, OnInit, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChartService, AlgorithmComparisonChart } from '../services/chart.service';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

@Component({
  selector: 'app-summary',
  standalone: true,
  imports: [CommonModule],
  template: `
    <h1>Summary</h1>

    <section aria-labelledby="chart-heading">
      <h2 id="chart-heading">{{ chartData?.title || 'Algorithm Comparison' }}</h2>
      <div class="chart-container">
        <canvas #chartCanvas aria-label="Bar chart comparing voting algorithms"></canvas>
      </div>
      <p class="description">{{ chartData?.description }}</p>
      <p *ngIf="chartData?.source_url">
        <strong>Source:</strong>
        <a [href]="chartData!.source_url" target="_blank" rel="noopener">{{ chartData!.source_url }}</a>
      </p>
    </section>
  `,
  styles: [`
    h1 { margin-bottom: 20px; }
    h2 { margin-bottom: 15px; }
    .chart-container {
      max-width: 600px;
      margin: 20px 0;
    }
    .description {
      line-height: 1.6;
      margin: 20px 0;
    }
    a { color: #0066cc; }
  `]
})
export class SummaryComponent implements OnInit, AfterViewInit {
  @ViewChild('chartCanvas') chartCanvas!: ElementRef<HTMLCanvasElement>;
  chartData: AlgorithmComparisonChart | null = null;
  private chart: Chart | null = null;

  constructor(private chartService: ChartService) {}

  ngOnInit() {
    this.chartService.getAlgorithmComparison().subscribe({
      next: (data) => {
        this.chartData = data;
        this.renderChart();
      },
      error: (err) => console.error('Failed to load chart data:', err)
    });
  }

  ngAfterViewInit() {
    if (this.chartData) {
      this.renderChart();
    }
  }

  private renderChart() {
    if (!this.chartCanvas || !this.chartData) return;

    if (this.chart) {
      this.chart.destroy();
    }

    const ctx = this.chartCanvas.nativeElement.getContext('2d');
    if (!ctx) return;

    const algorithms = this.chartData.data.map(d => d.algorithm);
    const candidates = Object.keys(this.chartData.data[0].scores);

    const datasets = candidates.map((candidate, index) => ({
      label: `Candidate ${candidate}`,
      data: this.chartData!.data.map(d => d.scores[candidate]),
      backgroundColor: ['#4CAF50', '#2196F3', '#FF9800'][index % 3]
    }));

    this.chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: algorithms,
        datasets
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Scores by Algorithm (Winner highlighted)'
          },
          legend: {
            position: 'top'
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Score'
            }
          }
        }
      }
    });
  }
}
