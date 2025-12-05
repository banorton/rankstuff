import { Component, OnInit, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChartService, VoteDistributionChart } from '../services/chart.service';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule],
  template: `
    <h1>Reports</h1>

    <section aria-labelledby="chart-heading">
      <h2 id="chart-heading">{{ chartData?.title || 'Vote Distribution' }}</h2>
      <div class="chart-container">
        <canvas #chartCanvas aria-label="Stacked bar chart showing vote distribution"></canvas>
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
export class ReportsComponent implements OnInit, AfterViewInit {
  @ViewChild('chartCanvas') chartCanvas!: ElementRef<HTMLCanvasElement>;
  chartData: VoteDistributionChart | null = null;
  private chart: Chart | null = null;

  constructor(private chartService: ChartService) {}

  ngOnInit() {
    this.chartService.getVoteDistribution().subscribe({
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

    const options = this.chartData.data.map(d => d.option);

    this.chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: options,
        datasets: [
          {
            label: '1st Place Votes',
            data: this.chartData.data.map(d => d.first),
            backgroundColor: '#4CAF50'
          },
          {
            label: '2nd Place Votes',
            data: this.chartData.data.map(d => d.second),
            backgroundColor: '#2196F3'
          },
          {
            label: '3rd Place Votes',
            data: this.chartData.data.map(d => d.third),
            backgroundColor: '#FF9800'
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Distribution of Rankings by Option'
          },
          legend: {
            position: 'top'
          }
        },
        scales: {
          x: {
            stacked: true
          },
          y: {
            stacked: true,
            beginAtZero: true,
            title: {
              display: true,
              text: 'Number of Votes'
            }
          }
        }
      }
    });
  }
}
