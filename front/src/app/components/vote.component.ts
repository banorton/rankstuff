import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { CdkDragDrop, DragDropModule, moveItemInArray } from '@angular/cdk/drag-drop';
import { PollService, Poll, PollOption, RankedChoice, PollResults } from '../services/poll.service';

@Component({
  selector: 'app-vote',
  standalone: true,
  imports: [CommonModule, DragDropModule],
  template: `
    <div class="vote-page">
      <header class="vote-header">
        <a href="/" class="logo">rankstuff.io</a>
      </header>

      <div *ngIf="loading" class="loading">Loading poll...</div>

      <div *ngIf="error" class="error-message">{{ error }}</div>

      <div *ngIf="poll && !loading" class="poll-container">
        <div class="poll-header">
          <h1>{{ poll.title }}</h1>
          <div class="poll-meta">
            <span class="status" [class]="poll.status">{{ poll.status }}</span>
            <span>{{ poll.vote_count }} vote{{ poll.vote_count !== 1 ? 's' : '' }}</span>
          </div>
        </div>

        <!-- Voting (drag and drop) -->
        <div *ngIf="poll.status === 'open' && !hasVoted" class="vote-section">
          <p class="instructions">Drag to rank your choices (1 = most preferred)</p>
          <div cdkDropList (cdkDropListDropped)="drop($event)" class="rank-list">
            <div *ngFor="let opt of rankedOptions; let i = index" cdkDrag class="rank-item">
              <span class="rank-number">{{ i + 1 }}</span>
              <span class="rank-label">{{ opt.label }}</span>
              <div class="rank-controls">
                <button class="arrow-btn" (click)="moveUp(i)" [disabled]="i === 0">▲</button>
                <button class="arrow-btn" (click)="moveDown(i)" [disabled]="i === rankedOptions.length - 1">▼</button>
                <span class="drag-handle" cdkDragHandle>⠿</span>
              </div>
            </div>
          </div>
          <button (click)="submitVote()" class="btn-primary">Submit Vote</button>
          <p *ngIf="voteMessage" class="message error">{{ voteMessage }}</p>
        </div>

        <!-- Already voted -->
        <div *ngIf="hasVoted && poll.status === 'open'" class="voted-section">
          <p class="voted-message">✓ Your vote has been recorded!</p>
          <p class="thank-you">Thank you for participating.</p>
        </div>

        <!-- Poll not open -->
        <div *ngIf="poll.status === 'draft'" class="not-open">
          <p>This poll is not yet open for voting.</p>
        </div>

        <!-- Poll closed - show results -->
        <div *ngIf="poll.status === 'closed'" class="results-section">
          <div *ngIf="pollResults">
            <h2>Results</h2>
            <p class="results-meta">{{ pollResults.total_votes }} total vote{{ pollResults.total_votes !== 1 ? 's' : '' }}</p>
            <div class="results-list">
              <div *ngFor="let r of pollResults.results" class="result-item">
                <span class="result-rank">#{{ r.rank }}</span>
                <span class="result-label">{{ r.label }}</span>
                <span class="result-score">{{ r.score }} pts</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .vote-page {
      min-height: 100vh;
      background: #f5f5f5;
      padding: 20px;
    }

    .vote-header {
      text-align: center;
      margin-bottom: 30px;
    }

    .logo {
      font-size: 24px;
      font-weight: bold;
      color: #007bff;
      text-decoration: none;
    }

    .loading, .error-message {
      text-align: center;
      padding: 40px;
      font-size: 18px;
    }

    .error-message { color: #dc3545; }

    .poll-container {
      max-width: 500px;
      margin: 0 auto;
      background: white;
      border-radius: 8px;
      padding: 30px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    .poll-header {
      margin-bottom: 20px;
    }

    .poll-header h1 {
      margin: 0 0 10px;
      font-size: 24px;
    }

    .poll-meta {
      display: flex;
      gap: 10px;
      color: #666;
      font-size: 14px;
    }

    .status {
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 12px;
      text-transform: uppercase;
    }
    .status.draft { background: #ffc107; color: #000; }
    .status.open { background: #28a745; color: #fff; }
    .status.closed { background: #6c757d; color: #fff; }

    .instructions {
      color: #666;
      margin-bottom: 15px;
      font-size: 14px;
    }

    .vote-section { margin: 20px 0; }

    .rank-list {
      border: 1px solid #ddd;
      border-radius: 4px;
      margin-bottom: 20px;
    }

    .rank-item {
      display: flex;
      align-items: center;
      padding: 12px 15px;
      background: white;
      border-bottom: 1px solid #eee;
      cursor: move;
    }
    .rank-item:last-child { border-bottom: none; }
    .rank-item.cdk-drag-preview {
      box-shadow: 0 3px 10px rgba(0,0,0,0.2);
    }
    .rank-item.cdk-drag-placeholder {
      background: #f0f0f0;
    }

    .rank-number {
      width: 30px;
      height: 30px;
      background: #007bff;
      color: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      margin-right: 15px;
      flex-shrink: 0;
    }

    .rank-label { flex: 1; }

    .rank-controls {
      display: flex;
      align-items: center;
      gap: 5px;
    }

    .arrow-btn {
      background: none;
      border: 1px solid #ddd;
      border-radius: 3px;
      padding: 2px 6px;
      cursor: pointer;
      font-size: 10px;
      color: #666;
    }
    .arrow-btn:hover:not(:disabled) { background: #f0f0f0; }
    .arrow-btn:disabled { opacity: 0.3; cursor: not-allowed; }

    .drag-handle {
      color: #999;
      cursor: grab;
      font-size: 18px;
    }

    .btn-primary {
      background: #007bff;
      color: white;
      border: none;
      padding: 12px 24px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 16px;
      width: 100%;
    }
    .btn-primary:hover { background: #0056b3; }

    .voted-section {
      text-align: center;
      padding: 30px 0;
    }

    .voted-message {
      color: #28a745;
      font-size: 20px;
      font-weight: 500;
      margin: 0 0 10px;
    }

    .thank-you {
      color: #666;
    }

    .not-open {
      text-align: center;
      padding: 30px 0;
      color: #666;
    }

    .message { margin-top: 15px; }
    .message.error { color: #dc3545; }

    .results-section { margin-top: 20px; }
    .results-section h2 { margin: 0 0 10px; }
    .results-meta { color: #666; margin-bottom: 10px; font-size: 14px; }

    .results-list {
      border: 1px solid #ddd;
      border-radius: 4px;
    }

    .result-item {
      display: flex;
      align-items: center;
      padding: 12px 15px;
      border-bottom: 1px solid #eee;
    }
    .result-item:last-child { border-bottom: none; }

    .result-rank {
      font-weight: bold;
      width: 40px;
      color: #007bff;
    }
    .result-label { flex: 1; }
    .result-score { color: #666; }
  `]
})
export class VoteComponent implements OnInit {
  poll: Poll | null = null;
  rankedOptions: PollOption[] = [];
  hasVoted = false;
  voteMessage = '';
  pollResults: PollResults | null = null;
  loading = true;
  error = '';

  constructor(
    private pollService: PollService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      if (params['id']) {
        this.loadPoll(params['id']);
      }
    });
  }

  loadPoll(id: string) {
    this.loading = true;
    this.error = '';

    this.pollService.getPoll(id).subscribe({
      next: (poll) => {
        this.poll = poll;
        this.rankedOptions = [...poll.options];
        this.loading = false;

        if (poll.status === 'open') {
          this.pollService.checkVoted(id).subscribe({
            next: (res) => this.hasVoted = res.has_voted,
            error: () => {} // Ignore errors checking vote status
          });
        }

        if (poll.status === 'closed') {
          this.loadResults();
        }
      },
      error: () => {
        this.loading = false;
        this.error = 'Poll not found';
      }
    });
  }

  drop(event: CdkDragDrop<PollOption[]>) {
    moveItemInArray(this.rankedOptions, event.previousIndex, event.currentIndex);
  }

  moveUp(index: number) {
    if (index > 0) {
      moveItemInArray(this.rankedOptions, index, index - 1);
    }
  }

  moveDown(index: number) {
    if (index < this.rankedOptions.length - 1) {
      moveItemInArray(this.rankedOptions, index, index + 1);
    }
  }

  submitVote() {
    if (!this.poll) return;

    const rankings: RankedChoice[] = this.rankedOptions.map((opt, index) => ({
      option_id: opt.id,
      rank: index + 1
    }));

    this.pollService.vote(this.poll.id, rankings).subscribe({
      next: () => {
        this.voteMessage = '';
        this.hasVoted = true;
        // Refresh vote count
        this.pollService.getPoll(this.poll!.id).subscribe({
          next: (poll) => this.poll = poll
        });
      },
      error: (err) => {
        if (err.error?.detail?.includes('already voted')) {
          this.hasVoted = true;
        } else {
          this.voteMessage = err.error?.detail || 'Error submitting vote';
        }
      }
    });
  }

  loadResults() {
    if (!this.poll) return;
    this.pollService.getResults(this.poll.id).subscribe({
      next: (results) => this.pollResults = results,
      error: () => {} // Ignore errors loading results
    });
  }
}
