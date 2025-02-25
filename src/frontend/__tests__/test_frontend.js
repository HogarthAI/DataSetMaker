import '@testing-library/jest-dom';
import { fireEvent, waitFor } from '@testing-library/dom';
import { JSDOM } from 'jsdom';
import fs from 'fs';
import path from 'path';

const html = fs.readFileSync(path.resolve(__dirname, './templates/index.html'), 'utf8');

let dom;
let container;

beforeEach(() => {
  dom = new JSDOM(html, { runScripts: 'dangerously' });
  container = dom.window.document.body;
});

test('cycleRole changes role correctly', () => {
  const button = container.querySelector('.role-button');
  expect(button.textContent.trim()).toBe('USER');
  
  fireEvent.click(button);
  expect(button.textContent.trim()).toBe('ASSISTANT');
  
  fireEvent.click(button);
  expect(button.textContent.trim()).toBe('SYSTEM');
  
  fireEvent.click(button);
  expect(button.textContent.trim()).toBe('USER');
});

test('collectMessages gathers message data correctly', () => {
  const messagesContainer = container.querySelector('#messages');
  messagesContainer.innerHTML = `
    <div class="message-row">
      <button class="role-button">USER</button>
      <input value="Hello">
    </div>
    <div class="message-row">
      <button class="role-button">ASSISTANT</button>
      <input value="Hi there!">
    </div>
  `;
  
  const messages = dom.window.collectMessages();
  expect(messages).toEqual([
    { role: 'user', content: 'Hello' },
    { role: 'assistant', content: 'Hi there!' }
  ]);
});

test('saveToDataset sends correct data', async () => {
  const datasetId = '123';
  const messagesContainer = container.querySelector('#messages');
  messagesContainer.innerHTML = `
    <div class="message-row">
      <button class="role-button">USER</button>
      <input value="Test message">
    </div>
  `;
  
  global.fetch = jest.fn(() =>
    Promise.resolve({
      json: () => Promise.resolve({ status: 'success' }),
    })
  );

  dom.window.saveToDataset(datasetId);
  
  await waitFor(() => {
    expect(global.fetch).toHaveBeenCalledWith(
      `/save-to-dataset/${datasetId}`,
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify([{ role: 'user', content: 'Test message' }]),
      })
    );
  });
});
