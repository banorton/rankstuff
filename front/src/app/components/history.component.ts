import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { PollService, Poll } from '../services/poll.service';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="history-page">
      <h1>Poll History</h1>
      <p *ngIf="polls.length === 0 && !loading" class="empty">No polls yet. Create your first poll!</p>
      <p *ngIf="loading" class="loading">Loading...</p>
      <div class="poll-list">
        <div *ngFor="let poll of polls" class="poll-item" (click)="viewPoll(poll.id)">
          <div class="poll-info">
            <span class="poll-title">{{ poll.title }}</span>
            <span class="poll-date">{{ formatDate(poll.created_at) }}</span>
          </div>
          <div class="poll-meta">
            <span class="status" [class]="poll.status">{{ poll.status }}</span>
            <span class="votes">{{ poll.vote_count }} vote{{ poll.vote_count !== 1 ? 's' : '' }}</span>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .history-page { width: 100%; }
    h1 { margin-bottom: 20px; }
    .empty, .loading { color: #666; }
    .poll-list { display: flex; flex-direction: column; gap: 10px; }
    .poll-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 15px;
      border: 1px solid #ddd;
      border-radius: 4px;
      cursor: pointer;
      transition: background 0.2s;
    }
    .poll-item:hover { background: #f5f5f5; }
    .poll-info { display: flex; flex-direction: column; gap: 4px; }
    .poll-title { font-weight: 500; }
    .poll-date { font-size: 12px; color: #666; }
    .poll-meta { display: flex; align-items: center; gap: 10px; }
    .status {
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 12px;
      text-transform: uppercase;
    }
    .status.draft { background: #ffc107; color: #000; }
    .status.open { background: #28a745; color: #fff; }
    .status.closed { background: #6c757d; color: #fff; }
    .votes { font-size: 12px; color: #666; }
  `]
})
export class HistoryComponent implements OnInit {
  polls: Poll[] = [];
  loading = true;

  constructor(private pollService: PollService, private router: Router) {}

  ngOnInit() {
    this.pollService.listPolls().subscribe({
      next: (polls) => {
        this.polls = polls.sort((a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  viewPoll(id: string) {
    this.router.navigate(['/poll', id]);
  }

  formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  }
}
