import { Component, OnInit, OnDestroy, ViewChild, ElementRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Subject, takeUntil } from 'rxjs';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatListModule } from '@angular/material/list';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { TextFieldModule } from '@angular/cdk/text-field';
import { ChatService, Message, ChatSession } from './chat.service';
import { MessageComponent } from './message.component';
import { ThemeService } from '../shared/theme.service';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatSidenavModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatTooltipModule,
    MatProgressSpinnerModule,
    MatListModule,
    MatSlideToggleModule,
    TextFieldModule,
    MessageComponent
  ],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss'
})
export class ChatComponent implements OnInit, OnDestroy {
  private chatService = inject(ChatService);
  private themeService = inject(ThemeService);
  private fb = inject(FormBuilder);

  @ViewChild('messagesContainer') messagesContainer!: ElementRef;
  @ViewChild('fileInput') fileInput!: ElementRef;

  messageForm: FormGroup;
  messages: Message[] = [];
  sessions: ChatSession[] = [];
  currentSession: ChatSession | null = null;
  isLoading = false;
  selectedFile: File | null = null;
  isDarkMode = false;
  isSidebarOpen = true;

  private destroy$ = new Subject<void>();

  constructor() {
    this.messageForm = this.fb.group({
      content: ['', Validators.required]
    });
  }

  ngOnInit(): void {
    // Show welcome message with sample questions
    this.showWelcomeMessage();

    // Subscribe to messages
    this.chatService.messages$
      .pipe(takeUntil(this.destroy$))
      .subscribe(messages => {
        this.messages = messages;
        setTimeout(() => this.scrollToBottom(), 100);
      });

    // Subscribe to sessions
    this.chatService.sessions$
      .pipe(takeUntil(this.destroy$))
      .subscribe(sessions => {
        this.sessions = sessions;
      });

    // Subscribe to current session
    this.chatService.currentSession$
      .pipe(takeUntil(this.destroy$))
      .subscribe(session => {
        this.currentSession = session;
      });

    // Subscribe to loading state
    this.chatService.isLoading$
      .pipe(takeUntil(this.destroy$))
      .subscribe(isLoading => {
        this.isLoading = isLoading;
      });

    // Subscribe to theme
    this.themeService.isDarkMode$
      .pipe(takeUntil(this.destroy$))
      .subscribe(isDark => {
        this.isDarkMode = isDark;
      });

    // Check window size for sidebar
    this.checkWindowSize();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onSubmit(): void {
    if (this.messageForm.valid && !this.isLoading) {
      const content = this.messageForm.value.content.trim();
      if (!content) return;

      const request = {
        content,
        session_id: this.currentSession?.id,
        file: this.selectedFile || undefined
      };

      // Clear the form immediately for better UX
      this.messageForm.reset();
      this.selectedFile = null;

      this.chatService.sendMessage(request).subscribe({
        next: () => {
          // Form already cleared above
        },
        error: (error) => {
          console.error('Error sending message:', error);
          // Optionally restore the message on error
          // this.messageForm.patchValue({ content });
        }
      });
    }
  }

  onEnterKey(event: KeyboardEvent): void {
    if (!event.shiftKey) {
      event.preventDefault();
      this.onSubmit();
    }
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
    }
  }

  removeFile(): void {
    this.selectedFile = null;
    if (this.fileInput) {
      this.fileInput.nativeElement.value = '';
    }
  }

  triggerFileInput(): void {
    this.fileInput.nativeElement.click();
  }

  newChat(): void {
    this.chatService.createNewSession();
  }

  loadSession(session: ChatSession): void {
    this.chatService.loadSession(session.id).subscribe();
    if (window.innerWidth < 768) {
      this.isSidebarOpen = false;
    }
  }

  deleteSession(event: Event, session: ChatSession): void {
    event.stopPropagation();
    if (confirm('Are you sure you want to delete this conversation?')) {
      this.chatService.deleteSession(session.id).subscribe();
    }
  }

  toggleTheme(): void {
    this.themeService.toggleTheme();
  }

  toggleSidebar(): void {
    this.isSidebarOpen = !this.isSidebarOpen;
  }

  private scrollToBottom(): void {
    try {
      if (this.messagesContainer) {
        const element = this.messagesContainer.nativeElement;
        element.scrollTop = element.scrollHeight;
      }
    } catch (err) {
      console.error('Error scrolling to bottom:', err);
    }
  }

  private checkWindowSize(): void {
    if (window.innerWidth < 768) {
      this.isSidebarOpen = false;
    }
  }

  private showWelcomeMessage(): void {
    const welcomeMessage = {
      id: 'welcome',
      content: `# Welcome to Interface Wizard! 👋

I'm your AI assistant for healthcare data integration. I can help you with HL7/FHIR operations using natural language.

**Here are some things you can ask me:**

- "Create a test patient named John Doe"
- "Create 10 patients with random data"
- "Create a patient with diabetes diagnosis"
- "Generate ADT message for patient admission"
- "Retrieve patient with MRN 12345"
- "Send HL7 observation result for patient"

**Features:**
- Natural language patient record creation
- HL7 v2.x message generation (ADT, ORU, QRY)
- FHIR R4 resource management
- Mirth Connect integration
- OpenEMR database interaction

Just type your request below and I'll help you!`,
      role: 'assistant' as const,
      timestamp: new Date()
    };

    this.messages = [welcomeMessage];
  }

  formatDate(date: Date): string {
    const now = new Date();
    const messageDate = new Date(date);
    const diffMs = now.getTime() - messageDate.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return messageDate.toLocaleDateString();
  }

  getSessionTitle(session: ChatSession): string {
    return session.title || 'New conversation';
  }
}
