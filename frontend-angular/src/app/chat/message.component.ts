import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MarkdownModule } from 'ngx-markdown';
import { Message } from './chat.service';

@Component({
  selector: 'app-message',
  standalone: true,
  imports: [CommonModule, MatIconModule, MarkdownModule],
  templateUrl: './message.component.html',
  styleUrl: './message.component.scss'
})
export class MessageComponent {
  @Input() message!: Message;
}
