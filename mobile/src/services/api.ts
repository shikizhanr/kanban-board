import axios from 'axios';

const API_URL = 'https://jsonplaceholder.typicode.com';

export interface Post {
  userId: number;
  id: number;
  title: string;
  body: string;
}

export const getPosts = async (): Promise<Post[]> => {
  try {
    const response = await axios.get<Post[]>(`${API_URL}/posts`);
    return response.data;
  } catch (error) {
    console.error('Error fetching posts:', error);
    throw error; // Re-throw to allow caller to handle
  }
};

export const getPostById = async (id: number): Promise<Post> => {
  try {
    const response = await axios.get<Post>(`${API_URL}/posts/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching post with id ${id}:`, error);
    throw error; // Re-throw to allow caller to handle
  }
};
