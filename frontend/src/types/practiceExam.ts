export interface PracticeQuestion {
  id: string;
  topic: string;
  content: string;
  choices: string[];
  correct_index: number;
  explanation: string;
}

export interface PracticeBank {
  bank_code: string;
  title: string;
  language: string;
  version: number;
  questions: PracticeQuestion[];
}
