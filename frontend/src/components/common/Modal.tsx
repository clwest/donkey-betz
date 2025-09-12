import { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  maxWidth?: string;
  actions?: React.ReactNode;
}

export function Modal({ 
  isOpen, 
  onClose, 
  title, 
  children,
  size = 'lg',
  maxWidth,
  actions
}: ModalProps) {
  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl'
  };

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/90 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel 
                className={`
                  w-full ${maxWidth || sizeClasses[size]} transform overflow-hidden 
                  rounded-lg bg-black border-2 border-cyan-500/50
                  p-6 text-left align-middle transition-all relative
                  shadow-[0_0_20px_rgba(0,255,255,0.3)] shadow-cyan-500/30
                  before:absolute before:inset-0 before:border-2 before:border-cyan-500/30 before:rounded-lg before:animate-pulse
                `}
              >
                {/* Gaming corner decorations */}
                <div className="absolute top-2 left-2 w-3 h-3 border-l-2 border-t-2 border-cyan-500 z-10" />
                <div className="absolute top-2 right-2 w-3 h-3 border-r-2 border-t-2 border-cyan-500 z-10" />
                <div className="absolute bottom-2 left-2 w-3 h-3 border-l-2 border-b-2 border-cyan-500 z-10" />
                <div className="absolute bottom-2 right-2 w-3 h-3 border-r-2 border-b-2 border-cyan-500 z-10" />
                
                {title && (
                  <div className="flex items-center justify-between mb-4 border-b border-cyan-500/30 pb-4 relative">
                    <Dialog.Title
                      as="h3"
                      className="text-lg font-bold text-cyan-400 uppercase font-mono tracking-wider drop-shadow-[0_0_8px_rgba(0,255,255,0.5)]"
                    >
                      {title}
                    </Dialog.Title>
                    {/* Subtle header glow line */}
                    <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-500 to-transparent" />
                    <div className="flex items-center gap-2">
                      {actions}
                      <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-cyan-400 transition-all duration-200 hover:drop-shadow-[0_0_8px_rgba(0,255,255,0.5)] hover:scale-110 p-1 rounded border border-transparent hover:border-cyan-500/50"
                      >
                        <XMarkIcon className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                )}

                <div className="mt-2">
                  {children}
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}