import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';

interface LoginResponse {
  access_token: string;
  token_type: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private apiUrl = environment.apiUrl;
  private tokenKey = 'access_token';
  private refreshInterval: ReturnType<typeof setInterval> | null = null;

  constructor(private http: HttpClient, private router: Router) {
    this.startTokenRefresh();
  }

  login(identifier: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/auth/login`, {
      identifier,
      password
    }).pipe(
      tap(response => {
        localStorage.setItem(this.tokenKey, response.access_token);
        this.startTokenRefresh();
      })
    );
  }

  logout(): void {
    this.stopTokenRefresh();
    localStorage.removeItem(this.tokenKey);
    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  getUserId(): string | null {
    const token = this.getToken();
    if (!token) return null;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.sub || null;
    } catch {
      return null;
    }
  }

  private startTokenRefresh(): void {
    this.stopTokenRefresh();
    if (!this.isLoggedIn()) return;

    // Refresh token every 50 minutes (token expires in 60)
    this.refreshInterval = setInterval(() => {
      this.refreshToken();
    }, 50 * 60 * 1000);
  }

  private stopTokenRefresh(): void {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
    }
  }

  private refreshToken(): void {
    const token = this.getToken();
    if (!token) return;

    const headers = new HttpHeaders({ 'Authorization': `Bearer ${token}` });
    this.http.post<LoginResponse>(`${this.apiUrl}/auth/refresh`, {}, { headers }).subscribe({
      next: (response) => {
        localStorage.setItem(this.tokenKey, response.access_token);
      },
      error: () => {
        this.logout();
      }
    });
  }
}
