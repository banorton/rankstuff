import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

export interface PollOption {
  id: string;
  label: string;
  description?: string;
}

export interface RankedChoice {
  option_id: string;
  rank: number;
}

export interface PollCreate {
  title: string;
  description?: string;
  options: PollOption[];
}

export interface VoteCreate {
  poll_id: string;
  rankings: RankedChoice[];
}

export interface Poll {
  id: string;
  title: string;
  description?: string;
  options: PollOption[];
  status: 'draft' | 'open' | 'closed';
  owner_id: string;
  created_at: string;
  closes_at?: string;
  vote_count: number;
}

export interface VoteResponse {
  id: string;
  poll_id: string;
  user_id: string;
  submitted_at: string;
}

export interface OptionResult {
  option_id: string;
  label: string;
  score: number;
  rank: number;
}

export interface PollResults {
  poll_id: string;
  title: string;
  total_votes: number;
  results: OptionResult[];
  calculated_at: string;
}

@Injectable({ providedIn: 'root' })
export class PollService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient, private auth: AuthService) {}

  private getHeaders(): HttpHeaders {
    const token = this.auth.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  listPolls(): Observable<Poll[]> {
    return this.http.get<Poll[]>(
      `${this.apiUrl}/polls`,
      { headers: this.getHeaders() }
    );
  }

  createPoll(poll: PollCreate): Observable<Poll> {
    return this.http.post<Poll>(
      `${this.apiUrl}/polls`,
      poll,
      { headers: this.getHeaders() }
    );
  }

  getPoll(id: string): Observable<Poll> {
    return this.http.get<Poll>(`${this.apiUrl}/polls/${id}`);
  }

  openPoll(id: string): Observable<Poll> {
    return this.http.post<Poll>(
      `${this.apiUrl}/polls/${id}/open`,
      {},
      { headers: this.getHeaders() }
    );
  }

  closePoll(id: string): Observable<Poll> {
    return this.http.post<Poll>(
      `${this.apiUrl}/polls/${id}/close`,
      {},
      { headers: this.getHeaders() }
    );
  }

  vote(pollId: string, rankings: RankedChoice[]): Observable<VoteResponse> {
    return this.http.post<VoteResponse>(
      `${this.apiUrl}/polls/${pollId}/vote`,
      { poll_id: pollId, rankings },
      { headers: this.getHeaders() }
    );
  }

  getResults(pollId: string): Observable<PollResults> {
    return this.http.get<PollResults>(
      `${this.apiUrl}/polls/${pollId}/results`,
      { headers: this.getHeaders() }
    );
  }

  checkVoted(pollId: string): Observable<{ has_voted: boolean }> {
    return this.http.get<{ has_voted: boolean }>(
      `${this.apiUrl}/polls/${pollId}/voted`,
      { headers: this.getHeaders() }
    );
  }
}
