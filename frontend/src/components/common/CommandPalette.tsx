import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Command } from 'cmdk';
import { 
  MagnifyingGlassIcon,
  HomeIcon,
  SparklesIcon,
  PhotoIcon,
  CpuChipIcon,
  DocumentIcon,
  PlusIcon,
} from '@heroicons/react/24/outline';

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  // Toggle command palette with Cmd+K
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };

    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  const runCommand = (command: () => void) => {
    setOpen(false);
    command();
  };

  return (
    <>
      {open && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setOpen(false)} />
          <div className="relative min-h-full flex items-start justify-center p-4 sm:p-20">
            <Command className="relative w-full max-w-2xl glass rounded-xl shadow-2xl overflow-hidden">
              <div className="flex items-center px-4 py-3 border-b border-white/10">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 mr-3" />
                <Command.Input
                  placeholder="Type a command or search..."
                  className="flex-1 bg-transparent text-white placeholder-gray-400 outline-none"
                />
              </div>
              <Command.List className="max-h-96 overflow-y-auto p-2">
                <Command.Empty className="px-4 py-8 text-center text-gray-400">
                  No results found.
                </Command.Empty>

                <Command.Group heading="Navigation" className="px-2 py-2 text-xs text-gray-400 uppercase">
                  <Command.Item
                    onSelect={() => runCommand(() => navigate('/dashboard'))}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-white/10 hover:text-white cursor-pointer"
                  >
                    <HomeIcon className="h-5 w-5" />
                    <span>Dashboard</span>
                  </Command.Item>
                  <Command.Item
                    onSelect={() => runCommand(() => navigate('/workflows'))}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-white/10 hover:text-white cursor-pointer"
                  >
                    <CpuChipIcon className="h-5 w-5" />
                    <span>Workflows</span>
                    <span className="ml-auto px-2 py-0.5 text-xs bg-gradient-primary text-white rounded-full">NEW</span>
                  </Command.Item>
                  <Command.Item
                    onSelect={() => runCommand(() => navigate('/studio'))}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-white/10 hover:text-white cursor-pointer"
                  >
                    <SparklesIcon className="h-5 w-5" />
                    <span>Studio</span>
                  </Command.Item>
                  <Command.Item
                    onSelect={() => runCommand(() => navigate('/gallery'))}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-white/10 hover:text-white cursor-pointer"
                  >
                    <PhotoIcon className="h-5 w-5" />
                    <span>Gallery</span>
                  </Command.Item>
                </Command.Group>

                <Command.Group heading="Actions" className="px-2 py-2 text-xs text-gray-400 uppercase">
                  <Command.Item
                    onSelect={() => runCommand(() => navigate('/workflows/new'))}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-white/10 hover:text-white cursor-pointer"
                  >
                    <PlusIcon className="h-5 w-5" />
                    <span>New Workflow</span>
                    <kbd className="ml-auto text-xs px-1.5 py-0.5 bg-dark-800 rounded">⌘W</kbd>
                  </Command.Item>
                  <Command.Item
                    onSelect={() => runCommand(() => navigate('/studio'))}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-white/10 hover:text-white cursor-pointer"
                  >
                    <SparklesIcon className="h-5 w-5" />
                    <span>Generate Content</span>
                    <kbd className="ml-auto text-xs px-1.5 py-0.5 bg-dark-800 rounded">⌘G</kbd>
                  </Command.Item>
                  <Command.Item
                    onSelect={() => runCommand(() => navigate('/research'))}
                    className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-white/10 hover:text-white cursor-pointer"
                  >
                    <DocumentIcon className="h-5 w-5" />
                    <span>Upload Research</span>
                    <kbd className="ml-auto text-xs px-1.5 py-0.5 bg-dark-800 rounded">⌘U</kbd>
                  </Command.Item>
                </Command.Group>
              </Command.List>
            </Command>
          </div>
        </div>
      )}
    </>
  );
}