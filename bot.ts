import axios from 'axios';
import * as fs from 'fs';

const TELEGRAM_API = `https://api.telegram.org/bot${process.env.TELEGRAM_TOKEN}`;

const sendMessage = async (chatId: number, text: string) => {
    await axios.post(`${TELEGRAM_API}/sendMessage`, {
        chat_id: chatId,
        text
    });
};

const sendPhoto = async (chatId: number, photo: string, caption: string) => {
    await axios.post(`${TELEGRAM_API}/sendPhoto`, {
        chat_id: chatId,
        photo,
        caption
    });
};

const registerVendor = async (chatId: number, vendorName: string) => {
    const vendors = loadVendors();
    if (!vendors[chatId]) {
        vendors[chatId] = vendorName;
        saveVendors(vendors);
        await sendMessage(chatId, `Vendor '${vendorName}' registered successfully!`);
    } else {
        await sendMessage(chatId, 'You are already registered as a vendor.');
    }
};

const loadVendors = () => {
    if (fs.existsSync('vendors.json')) {
        return JSON.parse(fs.readFileSync('vendors.json', 'utf8'));
    }
    return {};
};

const saveVendors = (vendors: any) => {
    fs.writeFileSync('vendors.json', JSON.stringify(vendors));
};

const loadShopRequests = () => {
    if (fs.existsSync('shop_requests.json')) {
        return JSON.parse(fs.readFileSync('shop_requests.json', 'utf8'));
    }
    return {};
};

const saveShopRequests = (shopRequests: any) => {
    fs.writeFileSync('shop_requests.json', JSON.stringify(shopRequests));
};

// Handle input from Python script
const args = process.argv.slice(2);
const command = args[0];
const chatId = parseInt(args[1]);

if (command.startsWith('/register ')) {
    const vendorName = command.slice(10);
    registerVendor(chatId, vendorName);
} else if (command === '/shop') {
    sendMessage(chatId, 'What would you like to purchase? Please upload an image of the item.');
} else {
    sendMessage(chatId, 'Unknown command. Use /register <vendor_name> to register or /shop to shop.');
}

