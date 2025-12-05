import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <nav aria-label="Main navigation">
      <span class="brand">B58</span>
      <a routerLink="/dashboard" routerLinkActive="active">Dashboard</a>
      <a routerLink="/summary" routerLinkActive="active">Summary</a>
      <a routerLink="/reports" routerLinkActive="active">Reports</a>
      <button (click)="logout()" class="logout-btn">Logout</button>
    </nav>
    <main>
      <router-outlet></router-outlet>
    </main>
  `,
  styles: [`
    nav {
      background: #333;
      padding: 10px 20px;
      display: flex;
      align-items: center;
      gap: 20px;
    }
    .brand {
      color: white;
      font-weight: bold;
      font-size: 1.2em;
      margin-right: 20px;
    }
    a {
      color: #ccc;
      text-decoration: none;
      padding: 5px 10px;
    }
    a:hover, a.active {
      color: white;
    }
    .logout-btn {
      margin-left: auto;
      background: none;
      border: 1px solid #ccc;
      color: #ccc;
      padding: 5px 15px;
      cursor: pointer;
    }
    .logout-btn:hover {
      background: #555;
      color: white;
    }
    main {
      padding: 20px;
      max-width: 900px;
      margin: 0 auto;
    }
  `]
})
export class LayoutComponent {
  constructor(private auth: AuthService) {}

  logout() {
    this.auth.logout();
  }
}
