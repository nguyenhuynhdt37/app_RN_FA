'use client';

import React, { useEffect } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Underline from '@tiptap/extension-underline';
import Strike from '@tiptap/extension-strike';
import Link from '@tiptap/extension-link';
import Image from '@tiptap/extension-image';
import Placeholder from '@tiptap/extension-placeholder';
import TaskList from '@tiptap/extension-task-list';
import TaskItem from '@tiptap/extension-task-item';
import TextAlign from '@tiptap/extension-text-align';
import { Markdown } from '@tiptap/markdown';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import { createLowlight, common } from 'lowlight';
import { 
  Bold, Italic, List, ListOrdered, Quote, 
  Undo, Redo, Heading1, Heading2, Heading3,
  Code, Image as ImageIcon, Link as LinkIcon,
  Minus, Strikethrough, AlignLeft, AlignCenter, 
  AlignRight, AlignJustify, CheckSquare, Underline as UnderlineIcon,
  FileText, Languages, Sparkles
} from 'lucide-react';
import './tiptap-editor.css';
import TurndownService from 'turndown';
import MarkdownIt from 'markdown-it';

const turndown = new TurndownService({
  codeBlockStyle: 'fenced',
  fence: '```',
});

const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true,
});

const parseMarkdownToHTML = (markdown: string): string => {
  if (!markdown) return '';
  return md.render(markdown);
};

const lowlight = createLowlight(common);

interface TiptapEditorProps {
  value: string;
  onChange: (markdown: string) => void;
  placeholder?: string;
}
export function TiptapEditor({ value, onChange, placeholder = 'Bắt đầu viết...' }: TiptapEditorProps) {
  const [isMarkdownMode, setIsMarkdownMode] = React.useState(false);
  const [markdownValue, setMarkdownValue] = React.useState(value || '');
  const lastSyncedValueRef = React.useRef<string>(value || '');

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        codeBlock: false,
      }),
      CodeBlockLowlight.configure({
        lowlight,
        HTMLAttributes: {
          class: 'tiptap-code-block',
        },
      }),
      Underline,
      Strike,
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'tiptap-link',
        },
      }),
      Image.configure({
        HTMLAttributes: {
          class: 'tiptap-image',
        },
      }),
      TaskList.configure({
        HTMLAttributes: {
          class: 'tiptap-task-list',
        },
      }),
      TaskItem.configure({
        nested: true,
      }),
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
      Placeholder.configure({
        placeholder,
      }),
    ],
    content: parseMarkdownToHTML(value || ''),
    onUpdate: ({ editor }) => {
      const html = editor.getHTML();
      const markdown = turndown.turndown(html);
      lastSyncedValueRef.current = markdown;
      setMarkdownValue(markdown);
      onChange(markdown);
    },
  });

  const handleToggleMarkdownMode = () => {
    if (isMarkdownMode) {
      if (editor) {
        editor.commands.setContent(parseMarkdownToHTML(markdownValue));
      }
    } else {
      if (editor) {
        const html = editor.getHTML();
        setMarkdownValue(turndown.turndown(html));
      }
    }
    setIsMarkdownMode(!isMarkdownMode);
  };

  const handleMarkdownChange = (newMarkdown: string) => {
    setMarkdownValue(newMarkdown);
    onChange(newMarkdown);
  };

  // Sync content if value changes externally
  useEffect(() => {
    if (!editor || isMarkdownMode || value === lastSyncedValueRef.current) return;
    
    editor.commands.setContent(parseMarkdownToHTML(value || ''), false);
    lastSyncedValueRef.current = value;
  }, [value, editor, isMarkdownMode]);

  if (!editor) return null;

  const ToolbarButton = ({ 
    onClick, 
    active = false, 
    disabled = false, 
    children, 
    title 
  }: { 
    onClick: () => void, 
    active?: boolean, 
    disabled?: boolean, 
    children: React.ReactNode,
    title?: string
  }) => (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`tiptap-toolbar-btn ${active ? 'active' : ''}`}
      title={title}
    >
      {children}
    </button>
  );

  return (
    <div className="tiptap-editor-wrapper">
      <div className="tiptap-toolbar">
        <ToolbarButton 
          onClick={() => editor.chain().focus().undo().run()} 
          disabled={!editor.can().undo()}
          title="Hoàn tác"
        >
          <Undo size={18} strokeWidth={2.5} />
        </ToolbarButton>
        <ToolbarButton 
          onClick={() => editor.chain().focus().redo().run()} 
          disabled={!editor.can().redo()}
          title="Làm lại"
        >
          <Redo size={18} strokeWidth={2.5} />
        </ToolbarButton>

        <div className="w-px h-4 bg-white/10 mx-1" />

        <ToolbarButton 
          onClick={() => editor.chain().focus().toggleBold().run()} 
          active={editor.isActive('bold')}
          title="In đậm"
        >
          <Bold size={18} strokeWidth={2.5} />
        </ToolbarButton>
        <ToolbarButton 
          onClick={() => editor.chain().focus().toggleItalic().run()} 
          active={editor.isActive('italic')}
          title="In nghiêng"
        >
          <Italic size={18} strokeWidth={2.5} />
        </ToolbarButton>
        <ToolbarButton 
          onClick={() => editor.chain().focus().toggleUnderline().run()} 
          active={editor.isActive('underline')}
          title="Gạch chân"
        >
          <UnderlineIcon size={18} strokeWidth={2.5} />
        </ToolbarButton>
        <ToolbarButton 
          onClick={() => editor.chain().focus().toggleStrike().run()} 
          active={editor.isActive('strike')}
          title="Gạch ngang"
        >
          <Strikethrough size={18} strokeWidth={2.5} />
        </ToolbarButton>

        <div className="w-px h-4 bg-white/10 mx-1" />

        <ToolbarButton 
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()} 
          active={editor.isActive('heading', { level: 1 })}
          title="Tiêu đề 1"
        >
          <Heading1 size={18} strokeWidth={2.5} />
        </ToolbarButton>
        <ToolbarButton 
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()} 
          active={editor.isActive('heading', { level: 2 })}
          title="Tiêu đề 2"
        >
          <Heading2 size={18} strokeWidth={2.5} />
        </ToolbarButton>

        <div className="w-px h-4 bg-white/10 mx-1" />

        <ToolbarButton 
          onClick={() => editor.chain().focus().toggleBulletList().run()} 
          active={editor.isActive('bulletList')}
          title="Danh sách dấu chấm"
        >
          <List size={18} strokeWidth={2.5} />
        </ToolbarButton>
        <ToolbarButton 
          onClick={() => editor.chain().focus().toggleOrderedList().run()} 
          active={editor.isActive('orderedList')}
          title="Danh sách số"
        >
          <ListOrdered size={18} strokeWidth={2.5} />
        </ToolbarButton>
        <ToolbarButton 
          onClick={() => editor.chain().focus().toggleTaskList().run()} 
          active={editor.isActive('taskList')}
          title="Danh sách công việc"
        >
          <CheckSquare size={18} strokeWidth={2.5} />
        </ToolbarButton>

        <div className="w-px h-4 bg-white/10 mx-1" />

        <ToolbarButton 
          onClick={() => editor.chain().focus().setTextAlign('left').run()} 
          active={editor.isActive({ textAlign: 'left' })}
          title="Căn trái"
        >
          <AlignLeft size={18} strokeWidth={2.5} />
        </ToolbarButton>
        <ToolbarButton 
          onClick={() => editor.chain().focus().setTextAlign('center').run()} 
          active={editor.isActive({ textAlign: 'center' })}
          title="Căn giữa"
        >
          <AlignCenter size={18} strokeWidth={2.5} />
        </ToolbarButton>
        <ToolbarButton 
          onClick={() => editor.chain().focus().setTextAlign('justify').run()} 
          active={editor.isActive({ textAlign: 'justify' })}
          title="Căn đều"
        >
          <AlignJustify size={18} strokeWidth={2.5} />
        </ToolbarButton>

        <div className="w-px h-4 bg-white/10 mx-1" />

        <ToolbarButton 
          onClick={() => editor.chain().focus().toggleBlockquote().run()} 
          active={editor.isActive('blockquote')}
          title="Trích dẫn"
        >
          <Quote size={18} strokeWidth={2.5} />
        </ToolbarButton>
        <div className="w-px h-4 bg-white/10 mx-1" />

        <ToolbarButton 
          onClick={handleToggleMarkdownMode}
          active={isMarkdownMode}
          title={isMarkdownMode ? "Chế độ soạn thảo" : "Chế độ Markdown"}
        >
          <FileText size={18} strokeWidth={2.5} />
        </ToolbarButton>
      </div>

      <div className="tiptap-content">
        {isMarkdownMode ? (
          <textarea
            value={markdownValue}
            onChange={(e) => handleMarkdownChange(e.target.value)}
            placeholder={placeholder}
            className="tiptap-markdown-editor"
            spellCheck={false}
          />
        ) : (
          <EditorContent editor={editor} />
        )}
      </div>
    </div>
  );
}
