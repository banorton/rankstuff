import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { CdkDragDrop, DragDropModule, moveItemInArray } from '@angular/cdk/drag-drop';
import { PollService, Poll, PollOption, RankedChoice, PollResults } from '../services/poll.service';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-polls',
  standalone: true,
  imports: [CommonModule, FormsModule, DragDropModule],
  template: `
    <!-- CREATE MODE (default) -->
    <div *ngIf="!currentPoll" class="create-page">
      <section class="create-section" aria-labelledby="create-heading">
        <h1 id="create-heading">Create a Poll</h1>
        <form (ngSubmit)="createPoll()">
          <div class="form-group">
            <label for="title">Title</label>
            <input id="title" type="text" [(ngModel)]="newPoll.title" name="title"
                   placeholder="What should we vote on?" required />
          </div>
          <div class="form-group">
            <label for="description">Description (optional)</label>
            <input id="description" type="text" [(ngModel)]="newPoll.description" name="description"
                   placeholder="Add more context..." />
          </div>
          <div class="form-group">
            <label>Options (one per line, minimum 2)</label>
            <textarea [(ngModel)]="optionsText" name="options" rows="5"
                      placeholder="Option 1&#10;Option 2&#10;Option 3"></textarea>
          </div>
          <button type="submit" class="btn-primary" [disabled]="!canCreate()">Create Poll</button>
        </form>
        <p *ngIf="createMessage" class="message">{{ createMessage }}</p>
      </section>
    </div>

    <!-- VIEW/VOTE MODE -->
    <div *ngIf="currentPoll" class="poll-page">
      <div class="poll-header">
        <h1>{{ currentPoll.title }}</h1>
        <div class="poll-meta">
          <span class="status" [class]="currentPoll.status">{{ currentPoll.status }}</span>
          <span>{{ currentPoll.vote_count }} vote{{ currentPoll.vote_count !== 1 ? 's' : '' }}</span>
        </div>
      </div>
      <p *ngIf="currentPoll.description" class="poll-description">{{ currentPoll.description }}</p>

      <!-- Owner Actions -->
      <div class="owner-actions" *ngIf="currentPoll.status === 'draft'">
        <button (click)="openPoll()" class="btn-primary">Open Poll for Voting</button>
      </div>

      <!-- Voting (drag and drop) -->
      <div *ngIf="currentPoll.status === 'open' && !hasVoted" class="vote-section">
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
        <div class="vote-actions">
          <button (click)="submitVote()" class="btn-primary">Submit Vote</button>
          <button *ngIf="isOwner()" (click)="closePoll()" class="btn-secondary">Close Poll</button>
        </div>
      </div>

      <div *ngIf="hasVoted" class="voted-section">
        <p class="voted-message">✓ You have voted on this poll</p>
        <button *ngIf="isOwner() && currentPoll.status === 'open'" (click)="closePoll()" class="btn-secondary">Close Poll</button>
      </div>
      <p *ngIf="voteMessage" class="message">{{ voteMessage }}</p>

      <!-- Results -->
      <div *ngIf="pollResults" class="results-section">
        <h2>Results</h2>
        <p class="results-meta">{{ pollResults.total_votes }} total vote{{ pollResults.total_votes !== 1 ? 's' : '' }} · Borda Count</p>
        <div class="results-list">
          <div *ngFor="let r of pollResults.results" class="result-item">
            <span class="result-rank">#{{ r.rank }}</span>
            <span class="result-label">{{ r.label }}</span>
            <span class="result-score">{{ r.score }} pts</span>
          </div>
        </div>
      </div>

      <button *ngIf="!pollResults && (isOwner() || currentPoll.status === 'closed')" (click)="loadResults()" class="btn-secondary">View Results</button>

      <!-- Share Link -->
      <div class="share-section">
        <span class="share-label">Share this poll</span>
        <div class="share-input-wrapper">
          <input type="text" [value]="getPollUrl()" readonly #shareInput />
          <button (click)="copyLink(shareInput)" class="copy-btn">{{ copied ? 'Copied!' : 'Copy' }}</button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .create-page { max-width: 600px; }
    .create-section { margin-bottom: 40px; }
    h1 { margin-bottom: 20px; }
    h2 { margin: 20px 0 10px; }

    .form-group { margin-bottom: 15px; }
    .form-group label { display: block; margin-bottom: 5px; font-weight: 500; }
    .form-group input, .form-group textarea {
      width: 100%;
      padding: 10px;
      border: 1px solid #ccc;
      border-radius: 4px;
      font-size: 16px;
    }

    .btn-primary {
      background: #007bff;
      color: white;
      border: none;
      padding: 12px 24px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 16px;
    }
    .btn-primary:hover { background: #0056b3; }
    .btn-primary:disabled { background: #ccc; cursor: not-allowed; }

    .btn-secondary {
      background: #f0f0f0;
      color: #333;
      border: 1px solid #ccc;
      padding: 10px 20px;
      border-radius: 4px;
      cursor: pointer;
    }
    .btn-secondary:hover { background: #e0e0e0; }

    .message { color: #28a745; margin-top: 15px; }

    .poll-page { max-width: 600px; }
    .poll-header {
      display: flex;
      align-items: center;
      gap: 15px;
      margin-bottom: 10px;
    }
    .poll-header h1 { margin: 0; }
    .poll-description { color: #666; margin-bottom: 20px; }
    .poll-meta { display: flex; gap: 10px; color: #666; }
    .status {
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 14px;
      text-transform: uppercase;
    }
    .status.draft { background: #ffc107; color: #000; }
    .status.open { background: #28a745; color: #fff; }
    .status.closed { background: #6c757d; color: #fff; }

    .owner-actions { margin: 20px 0; }

    .vote-section { margin: 20px 0; }
    .vote-actions { display: flex; gap: 10px; }

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
    }
    .rank-label { flex: 1; }
    .rank-controls { display: flex; align-items: center; gap: 5px; }
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
    .drag-handle { color: #999; cursor: grab; }

    .voted-section {
      margin: 20px 0;
      display: flex;
      align-items: center;
      gap: 15px;
    }
    .voted-message {
      color: #28a745;
      font-weight: 500;
      margin: 0;
    }

    .results-section { margin: 20px 0; }
    .results-meta { color: #666; margin-bottom: 10px; }
    .results-list { border: 1px solid #ddd; border-radius: 4px; }
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

    .share-section {
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid #ddd;
      display: flex;
      align-items: center;
      gap: 15px;
    }
    .share-label {
      white-space: nowrap;
      font-weight: 500;
    }
    .share-input-wrapper {
      flex: 1;
      position: relative;
      display: flex;
    }
    .share-input-wrapper input {
      flex: 1;
      padding: 10px;
      padding-right: 70px;
      border: 1px solid #ccc;
      border-radius: 4px;
      font-family: monospace;
      font-size: 14px;
    }
    .copy-btn {
      position: absolute;
      right: 4px;
      top: 50%;
      transform: translateY(-50%);
      background: #007bff;
      color: white;
      border: none;
      padding: 6px 12px;
      border-radius: 3px;
      cursor: pointer;
      font-size: 13px;
    }
    .copy-btn:hover { background: #0056b3; }
  `]
})
export class PollsComponent implements OnInit {
  // Create poll
  newPoll = { title: '', description: '' };
  optionsText = '';
  createMessage = '';

  
  // View/vote poll
  currentPoll: Poll | null = null;
  rankedOptions: PollOption[] = [];
  hasVoted = false;
  voteMessage = '';
  pollResults: PollResults | null = null;
  copied = false;

  constructor(
    private pollService: PollService,
    private route: ActivatedRoute,
    private router: Router,
    private auth: AuthService
  ) {}

  ngOnInit() {
    // Check if we're viewing a specific poll via route param
    this.route.params.subscribe(params => {
      if (params['id']) {
        this.loadPoll(params['id']);
      }
    });
  }

  canCreate(): boolean {
    const lines = this.optionsText.split('\n').filter(l => l.trim());
    return !!this.newPoll.title && lines.length >= 2;
  }

  createPoll() {
    const options: PollOption[] = this.optionsText
      .split('\n')
      .filter(line => line.trim())
      .map((label, index) => ({
        id: String(index + 1),
        label: label.trim()
      }));

    this.pollService.createPoll({
      title: this.newPoll.title,
      description: this.newPoll.description || undefined,
      options
    }).subscribe({
      next: (poll) => {
        this.createMessage = '';
        this.newPoll = { title: '', description: '' };
        this.optionsText = '';
        this.router.navigate(['/poll', poll.id]);
      },
      error: (err) => {
        this.createMessage = 'Error: ' + (err.error?.detail || err.message);
      }
    });
  }

  loadPoll(id: string) {
    this.pollResults = null;
    this.hasVoted = false;
    this.voteMessage = '';

    this.pollService.getPoll(id).subscribe({
      next: (poll) => {
        this.currentPoll = poll;
        this.rankedOptions = [...poll.options];
        // Check if user has already voted
        if (poll.status === 'open') {
          this.pollService.checkVoted(id).subscribe({
            next: (res) => this.hasVoted = res.has_voted
          });
        }
      },
      error: () => {
        alert('Poll not found');
        this.router.navigate(['/create']);
      }
    });
  }

  openPoll() {
    if (!this.currentPoll) return;
    this.pollService.openPoll(this.currentPoll.id).subscribe({
      next: (poll) => this.currentPoll = poll,
      error: (err) => alert('Error: ' + (err.error?.detail || err.message))
    });
  }

  closePoll() {
    if (!this.currentPoll) return;
    this.pollService.closePoll(this.currentPoll.id).subscribe({
      next: (poll) => this.currentPoll = poll,
      error: (err) => alert('Error: ' + (err.error?.detail || err.message))
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
    if (!this.currentPoll) return;

    const rankings: RankedChoice[] = this.rankedOptions.map((opt, index) => ({
      option_id: opt.id,
      rank: index + 1
    }));

    this.pollService.vote(this.currentPoll.id, rankings).subscribe({
      next: () => {
        this.voteMessage = '';
        this.hasVoted = true;
        // Refresh vote count without resetting hasVoted
        this.pollService.getPoll(this.currentPoll!.id).subscribe({
          next: (poll) => this.currentPoll = poll
        });
      },
      error: (err) => {
        if (err.error?.detail?.includes('already voted')) {
          this.hasVoted = true;
        } else {
          this.voteMessage = 'Error: ' + (err.error?.detail || err.message);
        }
      }
    });
  }

  loadResults() {
    if (!this.currentPoll) return;
    this.pollService.getResults(this.currentPoll.id).subscribe({
      next: (results) => this.pollResults = results,
      error: (err) => alert('Error: ' + (err.error?.detail || err.message))
    });
  }

  getPollUrl(): string {
    return window.location.origin + '/poll/' + this.currentPoll?.id;
  }

  copyLink(input: HTMLInputElement) {
    navigator.clipboard.writeText(input.value);
    this.copied = true;
    setTimeout(() => this.copied = false, 2000);
  }

  isOwner(): boolean {
    if (!this.currentPoll) return false;
    const userId = this.auth.getUserId();
    return userId === this.currentPoll.owner_id;
  }
}
